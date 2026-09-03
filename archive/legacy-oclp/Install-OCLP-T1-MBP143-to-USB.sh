#!/bin/bash
# Install-OCLP-T1-MBP143-to-USB.sh
# Terminal interactive installer for macOS Tahoe

echo "=================================================="
echo "OCLP T1 MBP14,3 — USB EFI INSTALLER"
echo "=================================================="



echo "Verifica target OCLP-MBP143 in corso..."

# Find the external USB drive named OCLP-MBP143
TARGET_DISK=$(diskutil list | grep "OCLP-MBP143" | awk '{print $NF}' | head -n 1)
if [ -z "$TARGET_DISK" ]; then
    echo "ERRORE: Impossibile trovare un volume chiamato OCLP-MBP143."
    exit 1
fi

PARENT_DISK=$(diskutil info "$TARGET_DISK" | grep "Part of Whole" | awk '{print $4}')
if [ -z "$PARENT_DISK" ]; then
    echo "ERRORE: Impossibile determinare il disco parent per $TARGET_DISK."
    exit 1
fi

# Ensure it's not disk0, disk1, or disk2
if [[ "$PARENT_DISK" == "disk0" || "$PARENT_DISK" == "disk1" || "$PARENT_DISK" == "disk2" ]]; then
    echo "ERRORE CRITICO: Il target è su un disco di sistema ($PARENT_DISK). Operazione annullata per sicurezza."
    exit 1
fi

# Ensure it's external
IS_EXTERNAL=$(diskutil info "$PARENT_DISK" | grep "Device Location" | grep -c "External")
if [ "$IS_EXTERNAL" -eq 0 ]; then
    echo "ERRORE CRITICO: Il disco $PARENT_DISK non è un dispositivo esterno!"
    exit 1
fi

EFI_PARTITION=$(diskutil list "$PARENT_DISK" | grep "EFI" | awk '{print $NF}' | head -n 1)
if [ -z "$EFI_PARTITION" ]; then
    echo "ERRORE CRITICO: Impossibile trovare la partizione EFI sul disco $PARENT_DISK"
    exit 1
fi

echo ""
echo "Target: External USB ($PARENT_DISK)"
echo "Volume: OCLP-MBP143"
echo "EFI: $EFI_PARTITION"
echo "Model: MacBookPro14,3"
echo "TEST-B: ENABLED"
echo "WhateverGreen: 1.7.0"
echo "-wegnoegpu: ENABLED"
echo "T1: ENABLED"
echo "Wi-Fi: 14E4:43BA"
echo "Country: IT"
echo "=================================================="

read -p "Vuoi procedere con l'installazione su $PARENT_DISK e $EFI_PARTITION? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Operazione annullata dall'utente."
    exit 1
fi

echo "=================================================="
echo "FASE 1: PREPARAZIONE DATI SULLA PARTIZIONE PRINCIPALE"
echo "=================================================="
MAIN_VOL="/Volumes/OCLP-MBP143"

if [ ! -d "$MAIN_VOL" ]; then
    echo "Attendere il montaggio di $MAIN_VOL..."
    diskutil mount "$TARGET_DISK"
fi

if [ ! -d "$MAIN_VOL" ]; then
    echo "ERRORE: Impossibile montare il volume principale OCLP-MBP143."
    exit 1
fi

echo "Creazione cartelle di supporto..."
mkdir -p "$MAIN_VOL/Builds/Standard-Build"
mkdir -p "$MAIN_VOL/Builds/TEST-B-Build"
mkdir -p "$MAIN_VOL/Tools"
mkdir -p "$MAIN_VOL/Backups"
mkdir -p "$MAIN_VOL/Diagnostics"
mkdir -p "$MAIN_VOL/Documentation"

SRC_DIR="$(dirname "$0")"

echo "Copia dei tool e dei report..."
if [ -d "$SRC_DIR/Tools" ]; then
    cp -R "$SRC_DIR/Tools/"* "$MAIN_VOL/Tools/"
fi
if [ -d "$SRC_DIR/Build-Folder" ]; then
    # Copy builds if they exist in Build-Folder
    cp -R "$SRC_DIR/Build-Folder/"* "$MAIN_VOL/Builds/" 2>/dev/null || true
fi

echo ""
echo "=================================================="
echo "FASE 2: INSTALLAZIONE EFI"
echo "=================================================="

echo "Montaggio EFI in corso..."
diskutil mount "$EFI_PARTITION" || {
    echo "L'EFI non è formattata o è danneggiata. Formattazione in corso..."
    newfs_msdos -v EFI -F 32 /dev/r$EFI_PARTITION
    diskutil mount "$EFI_PARTITION"
}

if [ ! -d "/Volumes/EFI" ]; then
    echo "ERRORE: Mount della partizione EFI fallito."
    exit 1
fi

EFI_SRC_DIR="$SRC_DIR/Build-Folder/Standard-Build/EFI"
if [ ! -d "$EFI_SRC_DIR" ]; then
    EFI_SRC_DIR="$SRC_DIR/Build-Folder/TEST-B-Build/EFI"
fi
# Fallback to general if not using specific
if [ ! -d "$EFI_SRC_DIR" ]; then
    EFI_SRC_DIR="$SRC_DIR/EFI"
fi

if [ ! -d "$EFI_SRC_DIR" ]; then
    echo "ERRORE: Impossibile trovare la cartella EFI sorgente in $EFI_SRC_DIR."
    sleep 2
    diskutil unmount force "$EFI_PARTITION"
    exit 1
fi

echo "Pulizia EFI esistente..."
rm -rf /Volumes/EFI/EFI
rm -rf /Volumes/EFI/System

echo "Copia della EFI in corso da $EFI_SRC_DIR..."
cp -R "$EFI_SRC_DIR" /Volumes/EFI/

if [ ! -f "/Volumes/EFI/EFI/OC/config.plist" ]; then
    echo "ERRORE: Installazione fallita. config.plist mancante in EFI."
    sleep 2
    diskutil unmount force "$EFI_PARTITION"
    exit 1
fi

CONFIG_HASH=$(shasum -a 256 "/Volumes/EFI/EFI/OC/config.plist" | awk '{print $1}')
echo "CONFIG SHA256: $CONFIG_HASH"
echo "Installazione EFI completata con successo!"
echo "Smontaggio EFI..."
sleep 2
diskutil unmount force "$EFI_PARTITION"

echo "=================================================="
echo "OPERAZIONE COMPLETATA."
echo "Puoi ora riavviare tenendo premuto Option (Alt)."
echo "=================================================="
