#!/bin/bash
# =============================================================================
# collect_graphics_diagnostics.command
# Base + Track D AGDC extras (MC promote 30203ab).
# Does NOT rewrite EFI agdpmod (efi_builder out of scope).
# =============================================================================
# Safety: This script does NOT modify any system files, NVRAM, snapshots, or EFI.
# All output is written to a timestamped directory.
# =============================================================================

set -euo pipefail

TIMESTAMP=$(date "+%Y-%m-%d-%H-%M-%S")
OUTPUT_DIR="${HOME}/Desktop/GPU-Diagnostics-${TIMESTAMP}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "============================================="
echo "  GPU / Display Diagnostics (AGDC + WS)"
echo "============================================="
echo ""
echo "Output directory: ${OUTPUT_DIR}"
echo ""

mkdir -p "${OUTPUT_DIR}"

# --- System Info ---
echo ">>> Collecting system info..."
sw_vers > "${OUTPUT_DIR}/sw_vers.txt" 2>&1
uname -a > "${OUTPUT_DIR}/uname.txt" 2>&1
system_profiler SPHardwareDataType > "${OUTPUT_DIR}/hardware.txt" 2>&1

# --- GPU Info ---
echo ">>> Collecting GPU info..."
system_profiler SPDisplaysDataType > "${OUTPUT_DIR}/gpu_displays.txt" 2>&1

# --- IORegistry GPU dump ---
echo ">>> Dumping IORegistry GPU entries..."
ioreg -l -w 0 | grep -i -A 20 "class.*GPU\|class.*Display\|class.*Framebuffer\|class.*GFX\|IOGPUFamily" > "${OUTPUT_DIR}/ioreg_gpu.txt" 2>&1 || true

# --- Track D: AGDC / AppleGraphicsDevicePolicy / framebuffer ---
echo ">>> Collecting AGDC / AGDP / framebuffer clues..."
{
  echo "=== ioreg AppleGraphicsDevicePolicy / AGDC / framebuffer ==="
  ioreg -l -w 0 2>/dev/null | grep -i -E "AppleGraphicsDevicePolicy|AGDC|AGDP|Framebuffer|GFX0|pci-debug|compatible" | head -n 400 || true
  echo ""
  echo "=== ioreg AMD / Vega device-id snippets ==="
  ioreg -l -w 0 2>/dev/null | grep -i -E "ATY|AMD|687f|Vega|Radeon|PciRoot" | head -n 200 || true
} > "${OUTPUT_DIR}/agdc_ioreg.txt" 2>&1 || true

log show --predicate 'eventMessage CONTAINS[c] "AGDC" OR eventMessage CONTAINS[c] "AGDP" OR eventMessage CONTAINS[c] "AppleGraphicsDevicePolicy" OR eventMessage CONTAINS[c] "AGDCDiagnose" OR process CONTAINS[c] "AGDC"' --last 1h --style compact > "${OUTPUT_DIR}/agdc_logs.txt" 2>&1 || true

# solid AGDC vs UI-tint classification input (fill after observing the screen)
cat > "${OUTPUT_DIR}/agdc_yellow_symptoms_TEMPLATE.json" <<'EOF'
{
  "full_screen_solid_yellow": null,
  "ui_interactive": null,
  "ui_tint_only": null,
  "agdc_diagnose_yellow": null,
  "_readme": "solid+non-interactive => solid_agdc (framebuffer/agdpmod). interactive tint => ui_tint_compositor (ColorSync/SkyLight). Do not conflate."
}
EOF

# --- Kernel GPU logs ---
echo ">>> Collecting kernel GPU logs..."
log show --predicate 'subsystem == "com.apple.gpu" OR subsystem == "com.apple.iokit" OR eventMessage CONTAINS "GPU" OR eventMessage CONTAINS "gfx" OR eventMessage CONTAINS "Framebuffer"' --last 1h --style compact > "${OUTPUT_DIR}/kernel_gpu_logs.txt" 2>&1 || true

# --- WindowServer logs ---
echo ">>> Collecting WindowServer logs..."
log show --predicate 'process == "WindowServer"' --last 30m --style compact > "${OUTPUT_DIR}/windowserver_logs.txt" 2>&1 || true

# --- CoreDisplay logs ---
echo ">>> Collecting CoreDisplay logs..."
log show --predicate 'subsystem == "com.apple.CoreDisplay" OR process == "displaypolicyd"' --last 30m --style compact > "${OUTPUT_DIR}/coredisplay_logs.txt" 2>&1 || true

# --- SecurityAgent / loginwindow logs (boot/login issues) ---
echo ">>> Collecting SecurityAgent/loginwindow logs..."
log show --predicate 'process == "SecurityAgent" OR process == "loginwindow"' --last 30m --style compact > "${OUTPUT_DIR}/login_logs.txt" 2>&1 || true

# --- Kext list (graphics-related) ---
echo ">>> Listing loaded graphics kexts..."
kextstat 2>/dev/null | grep -iE "gpu|graphics|display|framebuffer|whatevergreen|radeon|amd|intel|kdkless" > "${OUTPUT_DIR}/graphics_kexts.txt" 2>&1 || true

# --- Boot args ---
echo ">>> Checking boot-args..."
nvram boot-args 2>/dev/null > "${OUTPUT_DIR}/boot_args.txt" 2>&1 || echo "No boot-args set" > "${OUTPUT_DIR}/boot_args.txt"

# --- Track D: agdpmod / shikigva presence summary ---
{
  echo "=== agdpmod / shikigva presence (boot-args) ==="
  if grep -q "agdpmod=" "${OUTPUT_DIR}/boot_args.txt" 2>/dev/null; then
    echo "agdpmod: PRESENT in boot-args"
  else
    echo "agdpmod: NOT in boot-args (may still be DeviceProperties-only)"
  fi
  if grep -q "shikigva=" "${OUTPUT_DIR}/boot_args.txt" 2>/dev/null; then
    echo "shikigva: PRESENT in boot-args"
  else
    echo "shikigva: NOT in boot-args"
  fi
} > "${OUTPUT_DIR}/agdp_boot_args_summary.txt" 2>&1 || true

# --- Track D: x86 detect JSON (agdc_yellow_risk + framebuffer checklist) ---
echo ">>> Running python -m x86 detect --json (best-effort)..."
if command -v python3 >/dev/null 2>&1; then
  (
    cd "${REPO_ROOT}"
    PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:$PYTHONPATH}" python3 -m x86 detect --json
  ) > "${OUTPUT_DIR}/x86_detect.json" 2>"${OUTPUT_DIR}/x86_detect.stderr" || true
else
  echo "python3 not found" > "${OUTPUT_DIR}/x86_detect.stderr"
fi

# --- Summary ---
echo ""
echo "============================================="
echo "  Collection complete"
echo "============================================="
echo "Output saved to: ${OUTPUT_DIR}"
echo ""
echo "AGDC vs UI-tint: fill agdc_yellow_symptoms_TEMPLATE.json after observing the screen."
echo "Detect fields: agdc_yellow_risk, ui_tint_yellow_risk, agdc_framebuffer_checklist"
echo ""
echo "Files collected:"
ls -la "${OUTPUT_DIR}/"
echo ""
echo "Please share this directory for analysis."
