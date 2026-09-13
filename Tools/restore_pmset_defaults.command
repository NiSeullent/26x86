#!/bin/bash
# =============================================================================
# restore_pmset_defaults.command
# REVERT LIVELLO 1 FIX: Ripristina i valori di fabbrica di pmset
# =============================================================================

set -euo pipefail

echo "============================================================"
echo "  REVERT LIVELLO 1: Ripristino Valori Predefiniti macOS"
echo "============================================================"
echo ""
echo "Richiesta permessi di amministratore:"
sudo -v

echo "Ripristino configurazione di default..."
sudo pmset -a hibernatemode 3
sudo pmset -a standby 1
sudo pmset -a autopoweroff 1
sudo pmset -a powernap 1
sudo pmset -a proximitywake 1

echo ""
echo "============================================================"
echo "  CONFIGURAZIONE ATTUALE (pmset -g)"
echo "============================================================"
pmset -g

echo ""
echo ">> VALORI PREDEFINITI RIPRISTINATI!"
echo ""
