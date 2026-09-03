#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Installing 26x86 T1 for MacBookPro14,3..."
sudo installer -pkg "${DIR}/26x86.pkg" -target /
