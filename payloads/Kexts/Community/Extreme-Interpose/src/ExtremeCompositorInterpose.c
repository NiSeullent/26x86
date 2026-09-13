/*
 * ExtremeCompositorInterpose — Track I PoC (26x86)
 * Symbol-based DYLD_INTERPOSE. X86_EXTREME=1 required for non-passthrough.
 */

#include "ExtremeCompositorInterpose.h"

/* dyld-interposing.h removed from modern SDKs — local macro (Apple OSS). */
#ifndef DYLD_INTERPOSE
#define DYLD_INTERPOSE(_replacement, _replacee) \
    __attribute__((used)) static struct { \
        const void *replacement; \
        const void *replacee; \
    } _interpose_##_replacee __attribute__((section("__DATA,__interpose"))) = { \
        (const void *)(unsigned long)&_replacement, \
        (const void *)(unsigned long)&_replacee \
    };
#endif
#include <stdarg.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/sysctl.h>
#include <sys/types.h>
#include <unistd.h>

#if defined(__APPLE__)
#include <CoreGraphics/CGDisplayConfiguration.h>
#include <ColorSync/ColorSyncProfile.h>
#include <ColorSync/ColorSyncTransform.h>
#endif

static bool x86_env_truthy(const char *name) {
    const char *v = getenv(name);
    if (!v) return false;
    return strcmp(v, "1") == 0 || strcasecmp(v, "true") == 0
        || strcasecmp(v, "yes") == 0 || strcasecmp(v, "on") == 0;
}

static bool x86_extreme(void) { return x86_env_truthy(X86_ENV_EXTREME); }

static const char *avx_mode(void) {
    const char *m = getenv(X86_ENV_AVX_MODE);
    return (m && *m) ? m : "passthrough";
}

static const char *lut_mode(void) {
    const char *m = getenv(X86_ENV_LUT_MODE);
    return (m && *m) ? m : "off";
}

static void x86_log(const char *fmt, ...) {
    if (!x86_extreme()) return;
    FILE *fp = fopen("/tmp/26x86-extreme-interpose.log", "a");
    if (!fp) return;
    fprintf(fp, "[pid=%d] ", (int)getpid());
    va_list ap; va_start(ap, fmt); vfprintf(fp, fmt, ap); va_end(ap);
    fputc('\n', fp); fclose(fp);
}

static bool is_avx_sysctl_name(const char *name) {
    static const char *const keys[] = {
        "hw.optional.avx1_0", "hw.optional.avx2_0", "hw.optional.avx512f", NULL
    };
    for (const char *const *p = keys; *p; ++p)
        if (strcmp(name, *p) == 0) return true;
    return false;
}

static int spoof_avx_int_value(void) {
    const char *mode = avx_mode();
    if (strcasecmp(mode, "report1") == 0) return 1;
    if (strcasecmp(mode, "report0") == 0) return 0;
    return -1;
}

static int wrap_sysctlbyname(const char *name, void *oldp, size_t *oldlenp,
                             void *newp, size_t newlen) {
    if (x86_extreme() && name && is_avx_sysctl_name(name)) {
        int spoof = spoof_avx_int_value();
        if (spoof >= 0) {
            x86_log("sysctlbyname spoof %s -> %d", name, spoof);
            if (oldp && oldlenp && *oldlenp >= sizeof(int) && newp == NULL) {
                *(int *)oldp = spoof;
                *oldlenp = sizeof(int);
                return 0;
            }
        }
    }
    return sysctlbyname(name, oldp, oldlenp, newp, newlen);
}
DYLD_INTERPOSE(wrap_sysctlbyname, sysctlbyname)

static int wrap_sysctl(int *name, u_int namelen, void *oldp, size_t *oldlenp,
                       void *newp, size_t newlen) {
    return sysctl(name, namelen, oldp, oldlenp, newp, newlen);
}
DYLD_INTERPOSE(wrap_sysctl, sysctl)

#if defined(__APPLE__)

static CGError wrap_CGGetDisplayTransferByTable(
    CGDirectDisplayID display, uint32_t capacity,
    CGGammaValue *redTable, CGGammaValue *greenTable, CGGammaValue *blueTable,
    uint32_t *sampleCount) {
    const char *mode = lut_mode();
    CGError err = CGGetDisplayTransferByTable(
        display, capacity, redTable, greenTable, blueTable, sampleCount);
    if (x86_extreme() && (strcmp(mode, "log") == 0 || strcmp(mode, "identity") == 0))
        x86_log("CGGetDisplayTransferByTable display=%u err=%d mode=%s",
                (unsigned)display, (int)err, mode);
    return err;
}
DYLD_INTERPOSE(wrap_CGGetDisplayTransferByTable, CGGetDisplayTransferByTable)

static CGError wrap_CGSetDisplayTransferByTable(
    CGDirectDisplayID display, uint32_t tableSize,
    const CGGammaValue *redTable, const CGGammaValue *greenTable,
    const CGGammaValue *blueTable) {
    const char *mode = lut_mode();
    if (x86_extreme() && strcmp(mode, "identity") == 0 && tableSize > 0) {
        CGGammaValue *id_r = calloc(tableSize, sizeof(CGGammaValue));
        CGGammaValue *id_g = calloc(tableSize, sizeof(CGGammaValue));
        CGGammaValue *id_b = calloc(tableSize, sizeof(CGGammaValue));
        if (id_r && id_g && id_b) {
            for (uint32_t i = 0; i < tableSize; ++i) {
                CGGammaValue v = (tableSize == 1) ? (CGGammaValue)1.0
                    : ((CGGammaValue)i / (CGGammaValue)(tableSize - 1));
                id_r[i] = id_g[i] = id_b[i] = v;
            }
            x86_log("CGSetDisplayTransferByTable IDENTITY size=%u", (unsigned)tableSize);
            CGError err = CGSetDisplayTransferByTable(display, tableSize, id_r, id_g, id_b);
            free(id_r); free(id_g); free(id_b);
            return err;
        }
        free(id_r); free(id_g); free(id_b);
    }
    if (x86_extreme() && strcmp(mode, "log") == 0)
        x86_log("CGSetDisplayTransferByTable size=%u", (unsigned)tableSize);
    return CGSetDisplayTransferByTable(display, tableSize, redTable, greenTable, blueTable);
}
DYLD_INTERPOSE(wrap_CGSetDisplayTransferByTable, CGSetDisplayTransferByTable)

static ColorSyncProfileRef wrap_ColorSyncProfileCreateWithURL(
    CFURLRef url, CFErrorRef *error) {
    if (x86_extreme() && strcmp(lut_mode(), "off") != 0)
        x86_log("ColorSyncProfileCreateWithURL");
    return ColorSyncProfileCreateWithURL(url, error);
}
DYLD_INTERPOSE(wrap_ColorSyncProfileCreateWithURL, ColorSyncProfileCreateWithURL)

static ColorSyncTransformRef wrap_ColorSyncTransformCreate(
    CFArrayRef profileSequence, CFDictionaryRef options) {
    if (x86_extreme() && strcmp(lut_mode(), "off") != 0)
        x86_log("ColorSyncTransformCreate");
    return ColorSyncTransformCreate(profileSequence, options);
}
DYLD_INTERPOSE(wrap_ColorSyncTransformCreate, ColorSyncTransformCreate)

#endif

__attribute__((constructor))
static void x86_extreme_interpose_init(void) {
    if (!x86_extreme()) return;
    x86_log("ExtremeCompositorInterpose loaded avx=%s lut=%s", avx_mode(), lut_mode());
}
