# 26x86 — NextCore macOS 부팅 문서 → nextcore.crevision.kr 배포

## 목적
NextCore(26x86) macOS 부팅·설치 문서를 **나무마크(NamuMark)**로 변환해 `nextcore.crevision.kr`(OpenNamu 위키)에 자동 동기화.

## 스택
- PowerShell 동기화 스크립트 + Python 변환기
- 소스: `docs/` (마크다운) → 변환 → OpenNamu API(`/api/register`) → MySQL → 위키 렌더링
- 서버 구성: `scripts/Setup-NextCoreServer.ps1`

## 구조
```
docs/                      # 원본 마크다운 문서
scripts/
  Sync-NextCoreWiki.ps1   # 메인 동기화 (변경분만/전체/서버설치)
  convert_md_to_namu.py   # 마크다운 → 나무마크 변환
.github/workflows/
  nextcore-wiki-sync.yml  # push 시 자동 동기화
```

## 명령어
```powershell
# 변경분만 동기화 (기본)
.\scripts\Sync-NextCoreWiki.ps1

# 전체 재동기화
.\scripts\Sync-NextCoreWiki.ps1 -Full

# 위키 서버 최초 설치
.\scripts\Sync-NextCoreWiki.ps1 -SetupServer
```

## 변환 파이프라인
1. `docs/` 아래 `.md` 파일 변경 감지 (git diff)
2. `convert_md_to_namu.py`로 나무마크 변환 (헤더/표/코드블록/링크 등 매핑)
3. OpenNamu `/api/register` POST로 문서 등록/갱신
4. MySQL 저장 → `nextcore.crevision.kr` 렌더링

## 나무마크 변환 규칙 (`namu-mark` 스킬 참조)
- 헤더: `# ` → `= `, `## ` → `== `, `### ` → `=== `
- 코드블록: ```` ```lang ``` → `{{{#!lang ... }}}`
- 표: `| a | b |` → `|| a || b ||`
- 링크: `[text](url)` → `[[url|text]]`
- 이미지: `![alt](url)` → `{{{#attachment:alt|url}}}`

## GitHub Actions
`.github/workflows/nextcore-wiki-sync.yml` — `docs/` 변경 push 시 자동 실행 (워크플로 권한: `contents: read`, `actions: read`)

## 서버 구성 (`Setup-NextCoreServer.ps1`)
- OpenNamu + MySQL + nginx 설치
- `/api/register` 엔드포인트 활성화
- SSL/도메인 설정

## 위키 주소
https://nextcore.crevision.kr (미설치 시 서버 최초 설정 필요)

## 관련 스킬
- `nextcore-wiki` — 문서→위키 동기화 (나무마크 변환 포함)
- `nextcore-deploy` — 위키 배포·롤백
- `namu-mark` — 나무마크 문법 참조·변환 규칙

## 라이선스
문서 콘텐츠: 프로젝트별. 스크립트: 내부 도구.