# stage-K — 공유 CLI 병합 제안 (미적용)

Track K는 **공유 `x86/cli.py`를 수정하지 않습니다.**

동등 CLI는 이미 동작합니다:

```bash
python -m x86.profiles apply macpro5-vega64-tahoe
```

나중에 통합 담당이 `python -m x86 profile …` 별칭을 원하면, 아래만 추가하면 됩니다
(이 파일은 제안이며 자동 적용되지 않음):

```python
# build_parser() 안 — Track K 제안
profile = subparsers.add_parser("profile", help="E2E hardware profiles")
# … delegate to x86.profiles.__main__.main
```

또는:

```python
# cmd_profile → from x86.profiles.__main__ import main as profiles_main
```

detect JSON에 `recommended_profile`을 붙이려면 `x86.profiles.serialize_profile_match_fields`를
호출만 하면 됩니다 (Track K가 `cli.py`에 패치하지 않음).
