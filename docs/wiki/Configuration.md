# 26x86 설정

26x86은 **이전 OpenCore Legacy Patcher**와 설정·자동 패치·앱 설치 경로를 **공유하지 않습니다.**

> 이전 패처에서 전환: [Migration.md](./Migration.md)

---

## 설정 파일

| 항목 | 경로 |
|------|------|
| **사용자 설정** | `~/Library/Preferences/com.niseullent.26x86.plist` |
| JSON 설정 | `~/Library/Application Support/26x86/config.json` |
| 로그 | `~/Library/Logs/26x86/` |

설정은 **`/Users/Shared/`에 쓰지 않습니다.**

```bash
defaults read com.niseullent.26x86
python3 -m x86 status
```

---

## 앱·데이터 경로

| 범위 | 경로 |
|------|------|
| PKG 설치 앱 | `/Library/Application Support/26x86/` |
| 사용자 데이터 | `~/Library/Application Support/26x86/` |
| Applications | `/Applications/26x86.app` |

---

## 자동 패치 작업

PKG 설치 또는 루트 패치 활성화 시 등록되는 작업은 `com.niseullent.26x86.*` 이름을 사용합니다.

| 작업 | 역할 |
|------|------|
| `auto-patch` | 부팅 시 자동 루트 패치 확인 |
| `macos-update` | macOS 업데이트 후 패치 재적용 |
| `os-caching` | OS 캐싱 |
| `rsr-monitor` | 보안 응답 모니터링 |

**이전 패처의 자동 패치와 동시에 실행할 수 없습니다.**

---

## 설정 키

새 기능은 `26x86.*` 접두사를 사용합니다 (예: `26x86.auto_patch`, `26x86.verbose_logging`).

### Safari 26 Pre-AVX Fix (`config.json`)

MacPro5,1 EFI 빌드 때 RestrictEvents 1.1.8을 자동 주입합니다. 기본값은 켜짐입니다.

```json
"safari26_preavx_fix": true,
"auto_pre_avx_patch": true
```

둘 중 하나를 `false`로 두면 자동 적용을 끕니다. 상세: [Safari-PreAVX-Fix.md](./Safari-PreAVX-Fix.md) · [Pre-AVX-Mac-Pro.md](./Pre-AVX-Mac-Pro.md)

익명 사용 통계를 끄려면 앱 **설정**에서 비활성화하거나:

```bash
defaults write com.niseullent.26x86 DisableCrashAndAnalyticsReporting -bool true
```

---

## 이전 패처와 경로 비교

| 이전 패처 (레거시) | 26x86 |
|-------------------|--------|
| 공유 plist (`/Users/Shared/…`) | 사용자 Preferences 또는 `config.json` |
| `/Library/Application Support/Dortania/` | `/Library/Application Support/26x86/` |
| 이전 패처 자동 작업 | `com.niseullent.26x86.*` |

전환 절차: [Migration.md](./Migration.md)
