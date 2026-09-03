#include "ExtremeCompositorInterpose.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int SkyLightPluginEntry(void) {
    const char *ext = getenv(X86_ENV_EXTREME);
    if (ext && (strcmp(ext, "1") == 0 || strcasecmp(ext, "true") == 0)) {
        FILE *fp = fopen("/tmp/26x86-extreme-interpose.log", "a");
        if (fp) {
            fputs("SkyLightPluginEntry no-op (Track I shim)\n", fp);
            fclose(fp);
        }
    }
    return 0;
}
