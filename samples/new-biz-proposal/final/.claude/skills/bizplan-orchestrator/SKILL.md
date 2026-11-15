---
name: bizplan-orchestrator
description: "기능성 스포츠웨어 스타트업의 초기창업패키지 사업계획서를 만드는 에이전트 팀을 조율한다. context 자료 분석과 데이터 시각화 → 목차·작가 페르소나에 따른 집필 → 평가위원 심사·팩트체크와 수정 → mermaid 도해·AI 일러스트 → DOCX·PDF 조립까지 수행한다. '사업계획서 초안 작성', '사업계획서 만들어줘', '초창패 사업계획서', '정부지원사업 제안서', 'PSST 사업계획서' 요청에 사용하고, '사업계획서 다시 실행', '재실행', '수정', '보완', '업데이트', '3장만 다시', '그림만 다시', '심사 의견 반영', '이전 결과를 바탕으로 개선', '창업자 자료 반영' 같은 후속 요청에도 반드시 사용한다. 사업계획서와 무관한 이미지 한 장 생성이나 차트 한 장 그리기에는 사용하지 않는다."
---

# 사업계획서 하네스 오케스트레이터

**목표:** `context/`의 모든 자료를 근거로, `custom-instruction/`의 목차와 작가 페르소나를 지킨 초기창업패키지 사업계획서 초안을 차트·도해·일러스트와 함께 만든다. 모든 산출물은 `output/` 아래에 버전을 붙여 쌓고 덮어쓰지 않는다.

## 실행 모드: 혼합

| 단계 | 실행 모드 | 선택 이유 |
|------|----------|----------|
| 0~1 준비 | 메인이 직접 | 버전·자료 목록·그룹을 확정해야 다음 단계 프롬프트가 정해진다 |
| 2 자료 분석 | 서브에이전트 병렬 위임 | 자료 묶음이 미리 정해지고 결과만 받으면 된다. 에이전트 5명 규모라 워크플로 없이 한 메시지 병렬 호출로 충분하다 |
| 3~4 집필·검토·수정 | 지속형 에이전트 협업 | 집필가가 검토 의견을 받아 같은 맥락에서 고쳐야 하고, 검토자도 이전 라운드 이슈를 기억해야 재검토가 짧아진다 |
| 4 일러스트(병행) | 서브에이전트 위임(백그라운드) | 초안 r0의 그림 계획만 있으면 독립적으로 진행할 수 있다 |
| 5 동결 | 메인이 직접 | 해시로 본문을 고정해 도해·조립이 같은 본문을 읽게 한다 |
| 6 도해 | 서브에이전트 위임 | 동결된 본문을 한 번 도해로 옮기면 된다 |
| 7~8 조립·QA·보고 | 메인이 직접 + 스크립트 | 결정적인 변환과 최종 육안 점검 |

이 환경의 `Agent` 도구에는 `name` 매개변수가 없다. 지속형 에이전트는 실행할 때 돌려받는 **에이전트 ID**를 `run_meta.md`에 적어 두고 `SendMessage({to: ID})`로 다시 부른다. `SendMessage`는 지연 로딩 도구이므로 처음 쓰기 전에 `ToolSearch("select:SendMessage")`로 불러온다. 공유 작업 목록(TaskCreate 등)은 쓰지 않고 진행 상태는 `run_meta.md`에 기록한다.

## 경로 규칙

| 기호 | 값 |
|------|----|
| `{OUT}` | `output/01_사업계획서_초안` |
| `{N}` | 이번 실행 버전(1, 2, …) |
| `{WS}` | `{OUT}/_workspace/v{N}` — 중간 산출물 |
| 차트·도해·일러스트 | `{OUT}/assets/{charts,diagrams,illustrations}/…_v{N}.*` (`references/visual-system.md`) |
| 최종 문서 | `{OUT}/drafts/사업계획서_초안_v{N}.{md,html,pdf,docx}` + `_제출용` |
| 검토 보고서 | `{OUT}/reviews/심사검토보고서_v{N}.md` |
| 창업자 요청 | `{OUT}/drafts/창업자_입력요청_v{N}.md` |

`{WS}` 안의 파일 이름은 `{단계}_{에이전트}_{산출물}.{ext}`를 따른다. 어떤 파일도 덮어쓰지 않는다. 고칠 때는 라운드(`_r1`)나 버전(`_v2`)을 올린 새 파일을 쓴다.

## 에이전트 구성

| 역할 | `subagent_type` | 모델 | 스킬 | 주요 산출물 |
|------|----------------|------|------|-----------|
| 자료 분석가 ×4 | `source-analyst` | sonnet | context-analysis | `01_analyst-{그룹}_facts.md` |
| 데이터 분석가 | `data-analyst` | sonnet | data-file-analysis (+dataviz) | 차트 PNG, `01_data-analyst_insights.md`, `_assets.json` |
| 집필가 (지속형) | `bizplan-writer` | fable | bizplan-writing | 수치 시트, 그림 계획, `02_writer_draft_r{k}.md` |
| 평가위원 (지속형) | `bizplan-evaluator` | opus | bizplan-review | `03_evaluator_review_r{k}.md` |
| 팩트체커 (지속형) | `fact-checker` | opus | bizplan-review | `03_fact-checker_review_r{k}.md` |
| 일러스트레이터 | `illustration-artist` | opus | bizplan-illustration + gpt-image2 | 일러스트 PNG, 샷 리스트, `_assets.json` |
| 도해 디자이너 | `diagram-designer` | sonnet | mermaid-diagram | 도해 `.mmd`/`.png`, `_assets.json` |

모델은 각 정의 파일의 `model:`을 따른다(호출할 때 `model`을 따로 넘기지 않는다).

## 0단계: 기존 작업 확인

1. `ls {OUT}/_workspace/`로 기존 버전을 확인한다.
2. 요청을 분류한다.

| 상황 | 처리 |
|------|------|
| 기존 버전 없음, 또는 "새로 작성" | `{N}` = 1(또는 최대+1). 1단계부터 전체 실행 |
| 같은 세션에서 지속형 에이전트가 살아 있고 "○○ 고쳐줘" | 새 버전 없이 현재 `{WS}`에서 4단계 라운드를 하나 더 진행(SendMessage) 후 5~8단계를 새 이름(`_v{N}b`)으로 |
| 새 세션에서 부분 수정("3장만 다시", "그림만 다시", "심사 의견 반영", "창업자 자료 반영") | `{N}` = 최대+1. 아래 "이월" 후 필요한 단계만 실행 |
| `context/`에 자료가 추가·변경됨 | `{N}` = 최대+1. 바뀐 자료의 그룹만 2단계 재실행, 나머지 팩트 시트는 이월 |

**이월(부분 재실행):** 직전 버전 `{WS_prev}`에서 새 `{WS}`로 **복사**한다(이동·덮어쓰기 금지).
- `05_frozen_draft.md` → `00_prev_draft.md`, `05_frozen_numbers.md` → `00_prev_numbers.md`
- `01_*_facts*.md`, `01_data-analyst_insights.md` → 같은 이름
- 모든 `*_assets.json` → `00_prev-v{M}_{원래이름}` (`_assets.json`으로 끝나야 조립 스크립트가 읽는다). 다시 만드는 그림은 새 자산 목록이 나중에 읽혀 대체된다.
- 창업자가 새 자료를 주었으면 `{WS}/00_input/`에 복사하고 집필가 프롬프트에 경로를 넣는다.

3. `{WS}/run_meta.md`를 만든다: 버전, 날짜, 요청 원문, 분류, 기준 버전, 실행할 단계, 에이전트 ID(실행 후 기록), 단계별 상태.

## 1단계: 준비

```bash
mkdir -p "{WS}/00_extract" "{OUT}/assets/charts" "{OUT}/assets/diagrams" "{OUT}/assets/illustrations" "{OUT}/drafts" "{OUT}/reviews"
```

1. **자료 목록:** `ls context/`로 모든 파일을 나열하고 `run_meta.md`에 적는다. 한 건도 빠뜨리지 않는다(프로젝트 지시: 모든 파일을 빠짐없이 분석).
2. **그룹 배정:** 파일 이름 번호·주제로 나눈다. 한 그룹의 텍스트가 너무 많으면(PDF 합계 약 80k자 초과) 둘로 나눈다.

| 그룹 | 접두어 | 배정 기준 |
|------|--------|----------|
| market | `MKT` | 시장 현황·규모·성장·트렌드 보고서 |
| competitor | `CMP` | 경쟁사 동향, 제품 비교 리뷰, 경쟁 구도 마인드맵·이미지 |
| customer | `CUS` | 비즈니스 모델 캔버스, 소비자·라이프스타일 논문, 진입 전략 보고서 |
| gov | `GOV` | (웹) 해당 연도 초기창업패키지 공고·사업비 규정·평가 항목, 국내 스포츠웨어·애슬레저 공식 통계, 기능성 시험·GRS 인증 개요 |
| data | — | CSV·XLSX 등 표 데이터 → 데이터 분석가 |

3. **사전 점검:** `command -v uv npx pdftotext pdftoppm`, Chrome 존재, `.env`에 `OPENAI_API_KEY` 줄이 있는지(`grep -c '^OPENAI_API_KEY=' .env` — 값은 출력하지 않는다). 빠진 도구가 있으면 해당 단계의 대안을 `run_meta.md`에 적는다.

## 2단계: 자료 분석

**실행 모드:** 서브에이전트 병렬 위임 — 한 메시지에서 `Agent`를 5번 호출한다(분석가 4 + 데이터 1).

source-analyst 프롬프트 틀:

```
너는 source-analyst다. context-analysis 스킬 절차를 따른다.
- 실행 버전 N={N}, 작업 폴더 WS={WS}, 팩트 ID 접두어={접두어}, 그룹={그룹}
- 분석 자료(모든 페이지를 읽을 것): {파일 경로 목록 또는 웹 조사 주제}
- 사업계획서 목차: custom-instruction/사업계획서 목차.txt (활용 목차 번호를 달 때 참고)
- 출력: {WS}/01_analyst-{그룹}_facts.md (PDF 추출 중간 파일은 {WS}/00_extract/)
- 반환: 팩트 수, 등급별 개수, 핵심 팩트 5개, 충돌·공백 요약
```

gov 그룹에는 조사 주제를 구체적으로 준다: "올해(실행 날짜 기준 연도)와 직전 연도 초기창업패키지 공고의 지원 한도·협약기간·정부지원사업비/자부담 비율·비목·평가 항목·블라인드 규정·제출 분량", "국내 스포츠웨어·애슬레저 시장 규모 공식 통계(원출처 기관)", "기능성 의류 시험 항목과 국내 시험기관", "GRS 인증 요건".

data-analyst 프롬프트 틀:

```
너는 data-analyst다. data-file-analysis 스킬 절차를 따른다(dataviz 스킬 원칙 + 프로젝트 팔레트).
- N={N}, WS={WS}, OUT={OUT}
- 데이터 파일: {CSV·XLSX 경로 목록}
- 다른 자료와 규모를 비교할 수 있도록 context/의 시장 보고서 파일명 목록: {목록} (필요하면 열람)
- 출력: 차트 {OUT}/assets/charts/chart_{slug}_v{N}.png, {WS}/01_data-analyst_insights.md, {WS}/01_data-analyst_charts.py, {WS}/01_data-analyst_assets.json
- 반환: 차트 목록(ID·메시지·활용 목차), 신뢰도 경고, 핵심 인사이트
```

완료 알림을 모두 받은 뒤 각 산출 파일이 실제로 있는지 `ls`로 확인한다. 메인은 이미 맡긴 분석을 직접 다시 하지 않는다.

## 3단계: 집필 (r0)

**실행 모드:** 지속형 에이전트 — `bizplan-writer` 1명. 돌려받은 ID를 `run_meta.md`에 적는다.

```
너는 bizplan-writer다. bizplan-writing 스킬과 references/section-guide.md를 따르고,
custom-instruction/작가 페르소나.txt와 custom-instruction/사업계획서 목차.txt 원문을 먼저 읽어라.
- N={N}, WS={WS}, OUT={OUT}, 작성 기준일={오늘 날짜}
- 입력: {WS}/01_analyst-*_facts.md, {WS}/01_data-analyst_insights.md, {WS}/01_data-analyst_assets.json
  (부분 재실행이면: {WS}/00_prev_draft.md, 00_prev_numbers.md, 수정 범위={범위}, 창업자 자료={WS}/00_input/…)
- 출력: 02_writer_numbers.md, 02_writer_figure_plan.md, 02_writer_draft_r0.md, 02_writer_founder_requests.md (모두 {WS}/)
- 차트는 자산 목록의 그림 ID를 {{FIG:ID}}로 쓰고, 도해·일러스트는 그림 계획에 명세를 적어라.
- 첫 보고에 사용할 수 있는 도구 목록을 알려라. 완료 후에는 리더의 메시지를 기다려라.
```

완료 후 4개 파일이 있는지 확인한다. 본문에 목차의 모든 소목차 번호가 있는지 `grep -c '^#### '`로 대략 확인한다(정밀 확인은 평가위원 몫).

## 4단계: 검토·수정 루프 (최대 2라운드) + 일러스트 병행

**실행 모드:** 지속형 에이전트(평가위원·팩트체커 ↔ 리더 ↔ 집필가) + 서브에이전트(일러스트레이터, 백그라운드)

1. 한 메시지에서 세 에이전트를 실행한다.
   - `bizplan-evaluator`: "r0을 bizplan-review 스킬의 평가위원 심사 절차로 검토해 {WS}/03_evaluator_review_r0.md에 써라. 첫 보고에 도구 목록을 알려라."
   - `fact-checker`: "r0을 팩트체크 절차로 검토해 {WS}/03_fact-checker_review_r0.md에 써라. 첫 보고에 도구 목록(WebSearch·WebFetch 포함 여부)을 알려라."
   - `illustration-artist`: "bizplan-illustration 스킬로 {WS}/02_writer_figure_plan.md의 illustration 항목을 검토·생성하라. 본문은 {WS}/02_writer_draft_r0.md. N={N}, OUT={OUT}. 산출: 이미지, {WS}/03_illustration-artist_shotlist.md, {WS}/03_illustration-artist_assets.json. 반환: 목록·비용."
2. 두 검토가 끝나면 리더가 `{WS}/04_leader_review-merge_r{k}.md`를 쓴다: 두 판정, Critical·Major 목록, **서로 충돌하는 지적과 리더 결정**(예: 수치를 지우지 말고 `[창업자 입력 필요]`로 전환). 집필가가 혼자 충돌을 판단하지 않게 하기 위해서다.
3. `SendMessage(집필가 ID)`: "검토 파일 3개({WS}/03_evaluator_review_r{k}.md, 03_fact-checker_review_r{k}.md, 04_leader_review-merge_r{k}.md)를 반영해 r{k+1} 본문·수치 시트·변경 기록을 새 파일로 써라."
4. 수정본이 오면 재검토를 요청하기 전에 리더가 **시험 조립으로 실제 쪽수를 잰다.** 줄 수로 추정한 쪽수는 표 셀 줄바꿈·그림 배치 때문에 크게 틀린다(첫 실행에서 집필가 추정 13.7쪽 → 실측 17~18쪽). 아직 없는 도해는 스크립트가 임시 이미지로 채운다. `--width`에는 그림 계획의 폭을 넘긴다.
   ```bash
   uv run .claude/skills/bizplan-orchestrator/scripts/trial_layout.py --draft "{WS}/02_writer_draft_r{k+1}.md" \
     --manifests "{WS}/*_assets.json" --out-dir "{WS}/04_trial_r{k+1}" --width 그림ID=폭 ...
   ```
   그런 다음 `SendMessage(평가위원 ID)`와 `SendMessage(팩트체커 ID)`로 r{k+1} 재검토를 요청한다(이전 이슈 처리 확인 우선). 평가위원에게는 실측 쪽수와 시험 조립 PDF 경로를 함께 넘긴다.
5. 종료 조건: 두 검토가 모두 PASS이거나, 수정 2라운드(r2)를 마쳤을 때. r2 뒤에도 REVISE면 더 돌리지 않고 남은 이슈를 최종 보고서에 적는다. 라운드를 무한히 돌리면 비용만 늘고 문체가 흔들린다.
6. 집필가 변경 기록의 "영향받는 그림 ID"에 일러스트가 있으면 일러스트레이터에게 해당 샷만 다시 요청한다(새 실행, 이전 샷 리스트 경로 전달).

## 5단계: 본문 동결

```bash
cp "{WS}/02_writer_draft_r{최종}.md" "{WS}/05_frozen_draft.md"
cp "{WS}/02_writer_numbers{최신}.md" "{WS}/05_frozen_numbers.md"
shasum "{WS}/05_frozen_draft.md" "{WS}/05_frozen_numbers.md" > "{WS}/freeze_05.sha"
```

집필가·평가위원·팩트체커에게 SendMessage로 동결을 알린다: "본문을 동결했다. 이후 고칠 내용이 생기면 동결 파일을 고치지 말고 새 라운드 파일을 쓰고 리더에게 알려라."

- **마지막 라운드(r2)는 재검토와 병렬로 동결한다.** 재검토 결과와 관계없이 r2를 동결하기로 이미 정했으므로, 재검토를 기다리지 않고 6단계 도해를 시작해 시간을 줄인다.
- **동결 후 좁은 범위 패치(예외):** 최종 재검토에 수정 범위가 명확한 이슈(문구·산식·항목명 등 몇 줄)만 남으면 집필가에게 해당 이슈만 고친 `r{k+1}`을 요청한다. 리더는 `diff`로 바뀐 줄이 지시 범위뿐인지 확인하고, 수치를 다시 계산한 뒤 `05_frozen_draft_r{k+1}.md`와 새 해시 파일로 다시 동결한다. 패치가 도해에 들어간 수치를 바꾸면 해당 도해도 다시 만든다.
- 리더가 동결본을 직접 고칠 때(제목 표기 같은 편집 사항만)는 새 파일로 만들고 `05_leader_edit-log.md`에 전후 문구와 사유를 남긴다.

## 6단계: 도해 (+ 필요 시 차트 보완)

**실행 모드:** 서브에이전트 위임

- `diagram-designer`: "mermaid-diagram 스킬로 {WS}/02_writer_figure_plan.md의 diagram 항목을 {WS}/05_frozen_draft.md·05_frozen_numbers.md 기준으로 작성·렌더링·검수하라. N={N}, OUT={OUT}. 산출: .mmd/.png, {WS}/06_diagram-designer_assets.json."
- 그림 계획에 `chart` 유형 요청이 있거나 수치가 바뀌어 차트가 낡았으면 같은 메시지에서 `data-analyst`를 다시 실행한다(자산 목록은 `{WS}/06_data-analyst_assets.json`).
- 일러스트레이터 완료 알림도 이 단계 안에서 기다린다.

## 7단계: 조립과 최종 QA

먼저 **리더 최종 자산 목록**을 만든다. 각 제작 에이전트의 자산 목록에는 제작 당시 캡션이 들어 있다. 이 캡션은 검토 라운드에서 바뀐 표현(삭제된 주장, SKU 변경 등)을 반영하지 못한다. 그래서 그림 계획 최신본의 '확정 캡션' 표에서 캡션·출처·폭을 읽어 `{WS}/07_leader_final-captions_assets.json`에 쓴다. 파일 이름이 가장 뒤에 정렬되므로 같은 그림 ID의 값을 대체한다. 첫 실행에서는 이 단계가 빠진 시험 조립본에 검토에서 지운 문구가 캡션으로 다시 나타났다.

```bash
shasum -c "{WS}/freeze_05.sha"
uv run .claude/skills/bizplan-orchestrator/scripts/build_document.py \
  --draft "{WS}/05_frozen_draft.md" --manifests "{WS}/*_assets.json" \
  --out-dir "{OUT}/drafts" --name "사업계획서_초안_v{N}"
```

1. 해시가 다르면 무엇이 바뀌었는지 확인하고, 바뀐 본문으로 6단계를 다시 할지 정한다.
2. 빌드 보고서(`*_build_report.json`)의 `figures_missing`을 확인한다. 누락은 해당 에이전트에 한 번 재요청하고, 그래도 없으면 자리 표시로 두고 보고서에 적는다. `figures_used`의 파일 버전이 최종 채택본인지도 확인한다.
   - 제출용 PDF 텍스트에서 다음을 `grep`으로 확인한다.
     - AI 도구명(ChatGPT, Genspark, STORM 등)이 0건인지
     - 메모 표지(`심사위원 예상 질문`, `작성 메모`)가 0건인지
     - 검토에서 지운 핵심 표현이 다시 나타나지 않는지
     - 태그(`[확인 필요]`·`[창업자 입력 필요]`·`[가정]`) 개수 — 보고서에 적는다
3. **육안 QA:** `pdftoppm -r 50 -png "{OUT}/drafts/사업계획서_초안_v{N}_제출용.pdf" "{WS}/07_qa/page"`로 페이지 이미지를 만들고, 표지·각 대목차 첫 쪽·그림이 있는 쪽을 Read로 본다. 그림 잘림, 표 넘침, 빈 쪽, 글꼴 깨짐을 확인한다. 고칠 것이 있으면 원인(본문·그림·CSS)을 고쳐 `_v{N}b` 이름으로 다시 조립한다.
4. 대목차별 쪽수를 제출용 PDF에서 세어 목차 배분과 비교해 보고서에 적는다.
5. `{OUT}/reviews/심사검토보고서_v{N}.md`: 최종 라운드 판정·점수, 남은 이슈, 쪽수 점검, 그림 목록, 일러스트 비용, 누락 사항.
6. `{WS}/02_writer_founder_requests.md`를 `{OUT}/drafts/창업자_입력요청_v{N}.md`로 복사한다.

## 8단계: 보고

사용자에게 다음을 짧게 알린다: 최종 문서 경로(검토용·제출용), 판정과 남은 핵심 이슈, 그림 수(차트·도해·일러스트), 일러스트 비용, **창업자가 채워야 할 상위 항목**, 누락·실패 사항. `_workspace/`는 사후 검증용으로 남긴다.

## 데이터 전달

| 단계 경계 | 전달 방법 | 경로 |
|----------|----------|------|
| 1 → 2 | 프롬프트(자료 목록·그룹·경로) | `run_meta.md` |
| 2 → 3 | 파일 | `{WS}/01_*` |
| 3 → 4 | 파일 + SendMessage | `{WS}/02_*`, `03_*`, `04_leader_*` |
| 4 → 5 | 파일 동결 + 해시 | `05_frozen_*`, `freeze_05.sha` |
| 5 → 6 | 파일 | `05_frozen_*`, `02_writer_figure_plan.md` |
| 2·4·6 → 7 | 자산 목록 JSON | `{WS}/*_assets.json` |

## 오류 처리

| 상황 | 대응 |
|------|------|
| `Agent type '…' not found` (정의 파일을 이번 세션에 새로 만들었거나 고쳐서 아직 등록되지 않음) | `subagent_type: "general-purpose"`로 실행하고, 프롬프트 첫 줄에 "먼저 `.claude/agents/{이름}.md`를 Read로 읽고 그 역할·원칙·입출력 규칙대로 일하라"를 넣는다. `model`에는 정의 파일의 `model:` 값을 그대로 넘긴다. 새로 만든 정의 파일은 등록이 늦게 반영된다(첫 실행에서 수 분 뒤 "New agent types are now available" 알림 후 사용 가능했음). 등록 알림이 온 뒤의 단계부터는 원래 `subagent_type`을 쓴다 |
| 서브에이전트 실패·빈 결과 | 산출 파일을 열어 실제 진행 정도를 확인하고 한 번 다시 실행한다. 또 실패하면 그 자료 없이 진행하고 `run_meta.md`와 최종 보고서에 누락을 적는다 |
| 지속형 에이전트 무응답 | SendMessage로 상태를 묻고 다시 지시한다. 그래도 안 되면 같은 `subagent_type`을 새로 실행하고 이전 산출물 경로와 현재 라운드를 프롬프트로 넘긴다 |
| 사용량 한도·인증 만료·권한 거부 | 다시 시도하지 않는다. 부분 산출물을 확인하고 `run_meta.md`에 중단 지점을 적은 뒤 사용자에게 알린다(한도라면 풀리는 시각 포함). 메인은 직접 확인한 사실만 대신 채우고 에이전트의 판단을 추측해 쓰지 않는다 |
| gpt-image2 종료 코드 2(키 없음 등) | 재시도하지 않는다. 일러스트 자리는 자리 표시로 두고 사용자에게 `.env` 설정을 안내한다 |
| mermaid 렌더링 반복 실패 | 도해 디자이너가 단순한 유형으로 바꾼다. 그래도 실패하면 `.mmd` 원문을 보고서에 첨부하고 자리 표시로 둔다 |
| 검토 의견 충돌 | 리더가 `04_leader_review-merge`에 결정과 사유를 적는다. 데이터 충돌은 지우지 않고 출처와 함께 남긴다 |
| 절반 넘는 에이전트 실패 | 진행을 멈추고 사용자에게 계속할지 묻는다 |
| 조립 스크립트 종료 코드 2(덮어쓰기 거부) | 이름의 버전을 올린다. `--force`는 사용자가 덮어쓰기를 명시했을 때만 |

## 테스트 시나리오

### 정상 흐름
1. 사용자가 "사업계획서 초안 작성"을 요청한다. `_workspace/`가 없으므로 N=1로 시작한다.
2. 2단계에서 분석가 4명·데이터 분석가 1명이 팩트 시트 4개, 인사이트, 차트 2~4개를 만든다.
3. 3단계에서 집필가가 r0을 쓰고, 4단계에서 r0 검토 → r1 수정 → r1 재검토(PASS). 그동안 일러스트 3~5장이 만들어진다.
4. 5단계 동결, 6단계 도해 5~7개, 7단계 조립.
5. 예상 결과: `{OUT}/drafts/사업계획서_초안_v1.{md,html,pdf,docx}`와 `_제출용`, `{OUT}/reviews/심사검토보고서_v1.md`, `{OUT}/drafts/창업자_입력요청_v1.md`.

### 오류 흐름 — 일러스트 API 실패
1. 일러스트레이터가 gpt-image2 실행에서 종료 코드 2("OPENAI_API_KEY 가 없습니다")를 받는다.
2. 재시도하지 않고 빈 자산 목록과 사유를 반환한다.
3. 조립 시 `illust-*` 자리는 "[그림 삽입: … — 자산 없음]"으로 남고, 최종 보고서와 사용자 보고에 `.env` 설정 안내를 적는다.

### 오류 흐름 — 부분 재실행
1. 새 세션에서 사용자가 "창업자 자료(시험성적서) 반영해서 3장만 다시"를 요청한다.
2. N=2로 만들고 v1의 동결 본문·수치·팩트·자산 목록을 이월한다. 시험성적서는 `{WS}/00_input/`에 복사한다.
3. 2단계는 건너뛰고, 집필가가 3장만 수정한 r0을 쓴 뒤 4~8단계를 진행한다. 바뀌지 않은 그림은 v1 파일을 그대로 쓴다.
