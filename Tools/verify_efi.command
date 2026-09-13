#!/usr/bin/env bash

echo "=========================================="
echo "          EFI Verification Tool           "
echo "=========================================="
echo
echo "This tool helps you verify which EFI partitions contain OpenCore."
echo "No changes will be made to your system."
echo
echo "=== Currently Mounted EFI Partitions ==="
df -h | grep -i efi || echo "No EFI partitions currently mounted."
echo
echo "=== System Disks ==="
diskutil list | grep -E "EFI|Apple_APFS"
echo
echo "=== Instructions ==="
echo "To manually check an EFI partition:"
echo "1. Run: sudo diskutil mount diskXsY (e.g., disk0s1)"
echo "2. Open Finder or Terminal and check /Volumes/EFI/EFI/OC"
echo "3. Run: sudo diskutil unmount diskXsY when done"
echo
read -p "Press Enter to exit..."
