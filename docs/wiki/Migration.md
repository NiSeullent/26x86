# 이전 패처에서 26x86으로 전환

**OpenCore Legacy Patcher**(공식 패처), T2용 변형, Mod·Plus 등 **이전 패처**에서 26x86으로 옮길 때의 절차입니다.

> 설정: [Configuration.md](./Configuration.md)

---

## 무엇이 바뀌는가

| 영역 | 이전 패처 | 26x86 |
|------|-----------|--------|
| 사용자 설정 | 공유 plist 등 | Application Support의 `config.json` 또는 사용자 Preferences |
| 실행 | 구 GUI 스크립트 | `26x86.command` 또는 `python3 -m x86 wizard` |
| 자동 패치 | 이전 패처 전용 작업 | 26x86 전용 작업 |

---

## 권장 전환 순서

1. **백업** ([Warnings.md](./Warnings.md))
2. 이전 패처에서 **루트 패치 되돌리기**
3. 26x86 설치
4. `26x86.command` 또는 `python3 -m x86 wizard`
5. `python3 -m x86 detect --json` → `build` → `patch`
6. (선택) 이전 패처 앱·설정 정리

---

## 자동 설정 이전 (1회)

첫 실행 시 읽을 수 있는 이전 설정을 **한 번만** 가져옵니다. 이후 26x86 설정만 사용합니다.

```bash
python3 -m x86 status
```

---

## 이전 패처와 동시 사용 — **하지 마세요**

자동 패치를 동시에 켜 두면 충돌할 수 있습니다.

---

## 관련 문서

[Configuration.md](./Configuration.md) · [Installation-Notes.md](./Installation-Notes.md) · [T2-Mac-Notes.md](./T2-Mac-Notes.md)
