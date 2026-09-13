#!/bin/bash
# =============================================================================
# kdk_remove.command
# Interactive tool to remove installed Kernel Debug Kits
# =============================================================================

set -euo pipefail

echo "============================================="
echo "  OCLP T1 — KDK Removal Tool"
echo "============================================="

KDK_DIR="/Library/Developer/KDKs"

if [ ! -d "$KDK_DIR" ]; then
    echo "Nessuna directory KDK trovata ($KDK_DIR)."
    echo "Nessun KDK installato."
    exit 0
fi

# Find all KDKs
KDK_FILES=$(find "$KDK_DIR" -mindepth 1 -maxdepth 1 -type d)

if [ -z "$KDK_FILES" ]; then
    echo "Nessun KDK installato in $KDK_DIR."
    exit 0
fi

echo "KDK Installati trovati:"
echo ""

# Display each KDK with its size
while IFS= read -r kdk_path; do
    kdk_name=$(basename "$kdk_path")
    kdk_size=$(du -sh "$kdk_path" 2>/dev/null | awk '{print $1}')
    echo "- $kdk_name ($kdk_size)"
    echo "  Percorso: $kdk_path"
    echo ""
done <<< "$KDK_FILES"

echo "ATTENZIONE: Questa operazione eliminerà TUTTI i KDK elencati sopra."
echo "Questa operazione richiede i privilegi di amministratore."
echo ""
read -p "TYPE YES TO CONTINUE: " confirm

if [ "$confirm" != "YES" ]; then
    echo "Operazione annullata."
    exit 1
fi

echo "Rimozione in corso..."
for kdk_path in $KDK_FILES; do
    echo "Rimuovendo: $kdk_path"
    sudo rm -rf "$kdk_path"
done

echo "Tutti i KDK sono stati rimossi."
echo "============================================="
