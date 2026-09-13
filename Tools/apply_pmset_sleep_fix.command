#!/bin/bash
# =============================================================================
# apply_pmset_sleep_fix.command
# LIVELLO 1 FIX: Disabilita Standby profondo, Ibernazione e Darkwake in RAM
# =============================================================================
# Modifiche 100% reversibili e sicure a livello macOS (nessuna modifica a EFI)
# =============================================================================

set -euo pipefail

echo "============================================================"
echo "  LIVELLO 1 FIX: Ottimizzazione Sleep/Wake macOS per MBP14,3"
echo "============================================================"
echo ""
echo "Questo script configurerà il power management di macOS per:"
echo " 1. Mantenere lo stato attivo unicamente nella RAM (hibernatemode 0)"
echo " 2. Evitare il deep sleep PCIe / D3cold delle GPU (standby 0)"
echo " 3. Disattivare autopoweroff (autopoweroff 0)"
echo " 4. Disattivare i risvegli silenziosi in background (powernap 0, proximitywake 0)"
echo ""
echo "Richiesta permessi di amministratore:"
sudo -v

echo "Applicazione configurazione pmset..."
sudo pmset -a hibernatemode 0
sudo pmset -a standby 0
sudo pmset -a autopoweroff 0
sudo pmset -a powernap 0
sudo pmset -a proximitywake 0

# Rimuove il vecchio sleepimage per liberare spazio su disco (opzionale e sicuro)
if [ -f /var/vm/sleepimage ]; then
    echo "Pulizia vecchio /var/vm/sleepimage..."
    sudo rm -f /var/vm/sleepimage || true
fi

echo ""
echo "============================================================"
echo "  CONFIGURAZIONE ATTUALE (pmset -g)"
echo "============================================================"
pmset -g

echo ""
echo ">> LIVELLO 1 FIX APPLICATO CON SUCCESSO!"
echo "Ora puoi testare la chiusura del coperchio o lo sleep da Menu Apple."
echo ""
