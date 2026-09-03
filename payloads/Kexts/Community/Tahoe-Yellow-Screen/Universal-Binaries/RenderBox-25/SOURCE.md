# RenderBox-25 payload slot (Track E)

## License / provenance

| 항목 | 내용 |
|------|------|
| Binary | Apple proprietary ``default.metallib`` (RenderBox.framework) |
| Redistribution | **Do not commit** the metallib — gitignored under this tree |
| Upstream pattern | OCLP Metal 31001 / [PR #1176](https://github.com/dortania/OpenCore-Legacy-Patcher/pull/1176) |
| Authentic Tahoe | *Not published* on Dortania/YBronst/hackdoc/NiSeullent as of 2026-09-04 |

## Staging modes

1. **Authentic** — drop a real ``RenderBox-25`` tree from future PSP DRAFT / OCLP nightly.
2. **Provisional** — ``Tools/fetch_renderbox25.py --provisional-from-24`` copies
   Sequoia ``RenderBox-24`` MTLB here for **path / gate validation only**.
   Liquid Glass ABI may still be wrong on Tahoe; treat as research.

## Acquire

```bash
python Tools/fetch_renderbox25.py            # try public mirrors + DMGs
python Tools/fetch_renderbox25.py --provisional-from-24
python Tools/check_extreme_payloads.py
```
