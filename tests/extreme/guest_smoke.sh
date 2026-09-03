#!/usr/bin/env bash
# Guest smoke for Tahoe VM (UTM/qemu). Safe read-only / dry-run only.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
export X86_EXTREME="${X86_EXTREME:-1}"

echo "== host =="
sw_vers || true
uname -a || true

echo "== extreme validation (gates) =="
python3 -m x86.extreme.validation --gates-only

echo "== profile dry-run =="
python3 -m x86.profiles apply macpro5-vega64-tahoe --dry-run --extreme || \
  python3 -c "from x86.profiles.macpro5_vega64_tahoe import apply_profile; import json; print(json.dumps(apply_profile(dry_run=True, include_extreme=True), default=str, indent=2))"

echo "== done =="
