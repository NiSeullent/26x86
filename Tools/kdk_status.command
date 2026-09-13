#!/usr/bin/env bash

echo "=========================================="
echo "          KDK Status Diagnostics          "
echo "=========================================="
echo
echo "This script checks for the presence of Apple Kernel Debug Kits (KDKs)."
echo
echo "=== Installed KDKs ==="
ls -lah /Library/Developer/KDKs 2>/dev/null || echo "No KDKs found or directory does not exist."
echo
echo "=== KDK Info ==="
find /Library/Developer/KDKs -maxdepth 2 -type f \( -name "SystemVersion.plist" -o -name "Info.plist" \) -exec echo {} \; -exec cat {} \; 2>/dev/null | grep -A 1 -B 1 "ProductVersion\|BuildVersion" || echo "No detailed info available."
echo
read -p "Press Enter to exit..."
