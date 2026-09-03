# STAGE WORKFLOW (트랙 A 초안) — MC 통합 대기

> **파일:** `docs/STAGE-WORKFLOW.md.stage-A`  
> **작성:** 트랙 A  
> **상태:** stage only — **공유 `docs/STAGE-WORKFLOW.md` 직접 수정 금지**  
> **통합:** Mission Control(MC)만 최종 병합. 통합 후 재명령 대기.

이 문서는 병렬 트랙의 **파일 독재 금지** 규칙이다안이다. MC가 승인하면 `docs/STAGE-WORKFLOW.md`로 승격한다.

---

## 1. 목적

여러 에이전트/트랙이 같은 경로를 동시에 고치지 않도록, 모든 변경은 **스테이지 파일**에만 쓴다.  
공유 트리의 최종 내용은 **MC가 통합**한다.

---

## 2. 명명 규칙

| 항목 | 형식 |
|------|------|
| 스테이지 접미사 | `.stage-<TRACK>` |
| 트랙 A 예 | `docs/Foo.md.stage-A`, `x86/graphics/bar.py.stage-A` |
| 트랙 M 예 | `metal_3802.py.stage-M` |

- `<TRACK>` = 대문자 트랙 ID (`A` … `Z`).  
- **원본 경로 + `.stage-X`** = 그 트랙의 제안본/패치본.  
- 원본 `Foo.md` / `bar.py` 는 **해당 트랙이 직접 수정하지 않는다** (독재 금지).

### 예

```
docs/SkyLight-LUT-Tracks.md          ← 공유 (MC만 갱신)
docs/SkyLight-LUT-Tracks.md.stage-A  ← 트랙 A 제안
docs/Tahoe-Graphics-Roadmap.md.stage-A
opencore_legacy_patcher/.../metal_3802.py.stage-M
```

---

## 3. 트랙 의무

1. **공유 파일 직접 수정 금지** — `git add` 대상에 원본 공유 경로를 넣지 않는다.  
2. 변경은 오직 `*.stage-<자기트랙>` 에 작성·커밋.  
3. 커밋 메시지에 트랙 표기 (예: `docs(extreme-A): …`, `feat(skylight-M): …`).  
4. PR/푸시 후 **MC 통합 재명령을 기다린다** — 스스로 원본에 merge하지 않는다.  
5. 다른 트랙의 `.stage-*` 를 덮어쓰지 않는다.

---

## 4. MC (Mission Control) 통합

1. 관련 `*.stage-*` 수집·충돌 검토.  
2. 증거·가드·소유권 확인 후 원본으로 병합.  
3. 통합 커밋 (예: `chore(mc): merge stage-A Tracks …`).  
4. 병합된 stage 파일은 삭제 또는 `archived/` 로 이동 (MC 정책).  
5. 트랙에 **재명령** (다음 stage 작업).

트랙 A는 Mission Control **문서·조율**만 담당하며, 코드 원본 통합 실행은 MC 역할이다.  
(A가 만든 stage 문서도 MC가 원본으로 승격한다.)

---

## 5. 문서 vs 코드

| 종류 | stage 위치 | 비고 |
|------|------------|------|
| 문서 | `docs/*.md.stage-A` 등 | Tracks / Research / Roadmap / 본 워크플로 |
| 코드 | 원본과 동일 디렉터리에 `file.ext.stage-X` | M=`metal_3802.py.stage-M`, N=`non_metal.py.stage-N` |
| 위키 | `docs/wiki/Foo.md.stage-A` | 공유 wiki 직접 수정 금지 |

---

## 6. 3802 / Non-Metal (정책 요약 — 상세는 Tracks stage)

- **기본 경로:** Tahoe shared 가드 유지 (`return {}`).  
- **옵트인:** `X86_EXTREME=1` + `X86_TAHOE_3802=1` (트랙 M) / `X86_TAHOE_NONMETAL=1` (트랙 N).  
- 해금 **코드**는 M/N의 `.stage-M` / `.stage-N` 만. A는 문서 stage만.

---

## 7. 체크리스트 (트랙 커밋 전)

- [ ] 스테이징에 공유 원본 경로 없음  
- [ ] 모든 신규이 `*.stage-<TRACK>`  
- [ ] 다른 트랙 stage 미포함  
- [ ] MC 통합 대기 명시 (커밋 본문 또는 Tracks)

---

## 8. 변경 이력 (stage-A)

| 날짜 | 내용 |
|------|------|
| 2026-09-04 | 초안 — 파일 독재 금지 · `.stage-X` · MC 통합 |


---

## 9. 극한 실험 정책 (MC)

- **기본 배포**와 무관하게 `X86_EXTREME=1` 이면 L5(루트볼륨 바이너리 패치셋)·3802·Non-Metal·interpose·bytepatch 등 **모든 극한 실험 허용**.
- MC 문서/통합에 **"blocked forever" / 절대 금지 플래그를 넣지 않는다.**
- 기본 경로의 `return {}` 는 안전 기본값일 뿐, extreme 옵트인 해금을 막지 않는다.
