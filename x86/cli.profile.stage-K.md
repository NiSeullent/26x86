# stage-K — I apply_live 연계

공유 `cli.py` 미수정.

```bash
python -m x86.profiles apply macpro5-vega64-tahoe --extreme
python -m x86.profiles apply macpro5-vega64-tahoe --dry-run --extreme
```

`--extreme` → `macpro5_vega64_tahoe.run_interpose_apply` →
`interpose_apply.apply_extreme_interpose` (98e2528 / INTEGRATE 52f7298).

Mirror: `x86/profiles/extreme_interpose_link.stage-K.py`
