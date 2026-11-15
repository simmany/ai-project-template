---
name: mermaid-diagram
description: "사업계획서·제안서·보고서에 넣을 설득용 mermaid 도해(문제 구조, 해결 흐름, 공급망, 수익 흐름, 시장 진입 퍼널, TAM·SAM·SOM, 간트 일정, 협력 네트워크, ESG 순환)를 설계하고 한글 글꼴·프로젝트 팔레트로 PNG 렌더링한 뒤 육안 검수한다. mermaid 도해 작성, 다이어그램 그려줘, 흐름도·간트·조직도를 문서에 첨부, 도해 다시 그리기 요청이나 diagram-designer 에이전트 작업에 사용한다. 데이터 수치 차트는 data-file-analysis, 사진·일러스트는 gpt-image2·bizplan-illustration을 쓴다."
---

# 설득용 mermaid 도해

도해는 글로 다섯 줄 걸리는 구조를 한 장으로 3초 안에 이해시키기 위해 쓴다. 보기 좋은 그림보다 **한 장에 메시지 하나**가 우선이다.

## 1. 시작 전에 읽을 것

- 그림 계획(`{WS}/02_writer_figure_plan.md`)에서 유형이 `diagram`인 항목
- 동결된 본문(`{WS}/05_frozen_draft.md`)의 해당 소목차, 핵심 수치 시트(최신 라운드)
- 공통 시각 기준: `.claude/skills/bizplan-orchestrator/references/visual-system.md`

도해의 노드·수치·일정은 모두 본문과 수치 시트에서 가져온다. 본문에 없는 파트너명·수치·일정을 넣으면 본문과 도해가 어긋나고, 평가위원은 둘 다 의심한다.

## 2. 유형 선택

| 메시지 | 유형 | mermaid | 사업계획서 위치 예 |
|--------|------|---------|------------------|
| 원인 → 문제 → 고객 불편 | 문제 구조도 | `flowchart LR` + `subgraph` | 2.1.1 |
| 문제 ↔ 해결 1:1 대응 | 대응 매트릭스 | `flowchart LR` 두 열 | 1.1.2, 3.3.1 |
| 시장 범위 좁히기 | TAM → SAM → SOM 깔때기 | `flowchart TB` 세 단 | 2.2.1 |
| 개발 단계와 완료 기준 | 단계 흐름(stage-gate) | `flowchart LR` | 3.2.1 |
| 원단 → 봉제 → 검수 → 고객 | 공급망 | `flowchart LR` + 단계별 `subgraph` | 3.2.2 |
| 돈·제품의 흐름 | 수익 흐름(BM) | `flowchart LR`, 화살표 레이블에 수수료·비중 | 4.1.1 |
| 인지 → 체험 → 구매 → 재구매 | 진입 퍼널 | `flowchart TB` + 단계별 KPI | 4.2.1 |
| 단계 확장 조건 | 확장 로드맵 | `flowchart LR` 또는 `timeline` | 4.2.2 |
| 월별 일정 | 간트 | `gantt` | 4.3.1 |
| 내부 팀과 외부 협력 | 협력 네트워크 | `flowchart TB`, 중심 노드 + 주변 기관 | 5.2.2 |
| 자원 순환 | ESG 순환 | `flowchart LR` 순환 화살표 | 5.3.1 |

`quadrantChart`는 축 값의 근거가 있을 때만 쓴다. 데이터 기반 포지셔닝 맵은 데이터 분석가의 차트가 더 정확하다.

## 3. 스타일 규칙

- 노드 12개 이하. 넘으면 `subgraph`로 묶거나 두 장으로 나눈다.
- 노드 글자는 한 줄 12자 안팎, `<br/>`로 두 줄까지. 문장 대신 명사구.
- 수치는 노드나 화살표 레이블에 단위와 함께. `[가정]` 수치는 "(가정)", 협의 전 파트너는 "(협의 예정)"을 붙이고 `assume` 클래스로 점선 처리한다.
- 우리 회사·우리 제품 노드 하나에만 `our` 클래스(ACCENT)를 쓴다.
- 방향은 읽는 순서(왼쪽 → 오른쪽, 위 → 아래)를 따른다. 화살표가 교차하면 노드 순서를 바꾼다.
- 아래 클래스 정의를 flowchart 끝에 그대로 붙여 쓴다. 문서 전체 도해의 색이 같아진다.

```
classDef our fill:#F26B38,stroke:#C4511F,color:#FFFFFF,font-weight:bold;
classDef primary fill:#1B2A4A,stroke:#1B2A4A,color:#FFFFFF;
classDef soft fill:#E9EDF3,stroke:#1B2A4A,color:#1B2A4A;
classDef problem fill:#FBE9E5,stroke:#C8553D,color:#7A2E20;
classDef cool fill:#DCEEF5,stroke:#2E86AB,color:#14506A;
classDef eco fill:#E3F4EA,stroke:#3BAA6E,color:#1E5E3B;
classDef neutral fill:#F2F4F7,stroke:#8C96A8,color:#4A5568;
classDef assume fill:#FFFFFF,stroke:#8C96A8,stroke-dasharray:5 3,color:#4A5568;
```

간트 규칙: `dateFormat YYYY-MM`, `axisFormat %y.%m`, 섹션은 목표 단위(시제품·시험·마케팅·판매), 마일스톤은 1.2.1 목표와 같은 이름. 협약기간 시작·종료일은 공고 팩트를 따르고, 없으면 "M1~M10"처럼 상대 월로 쓴 뒤 캡션에 `[확인 필요: 협약기간]`을 적는다.

## 4. 렌더링

```bash
bash .claude/skills/mermaid-diagram/scripts/render_mermaid.sh <input.mmd> <output.png> [width=1600]
```

- 스크립트는 프로젝트 설정(`assets/mermaid-config.json`: 한글 글꼴·팔레트·간트 색)을 적용하고, 시스템 Chrome이 있으면 그것을 쓴다. 첫 실행은 `npx`가 mermaid-cli를 내려받느라 1~2분 걸린다.
- 출력 파일이 이미 있으면 덮어쓰지 않고 종료 코드 2로 멈춘다. 버전을 올려 다시 실행한다.
- 파일: `{OUT}/assets/diagrams/diagram_{slug}_v{N}.mmd`, 같은 이름의 `.png`

## 5. 검수

렌더링한 PNG를 Read로 직접 열어 확인한다. 코드만 보고 통과시키지 않는다. 한글 줄바꿈과 노드 크기는 렌더링해 봐야 알 수 있다.

- [ ] 글자 잘림·겹침·화살표 교차가 없다
- [ ] 문서 폭(가로 약 16cm)으로 줄였을 때 가장 작은 글자를 읽을 수 있다. 노드가 너무 많아 작아지면 나눈다
- [ ] 수치·명칭이 본문·수치 시트와 같다
- [ ] 메시지 하나가 3초 안에 읽힌다(캡션 문장과 그림이 같은 말을 한다)

결함이 있으면 `.mmd`를 고쳐 `_v{N}b`처럼 새 이름으로 다시 렌더링하고, 자산 목록에는 최종 파일만 등록한다.

## 6. 자산 목록

`{WS}/06_diagram-designer_assets.json`에 형식(`visual-system.md` 4절)대로 등록한다. `caption`은 결론 문장, `source`는 "본문 3.2.2 기준" 또는 수치 출처를 적는다. 가로로 긴 도해는 `width`를 `100%`, 세로로 긴 도해는 `60~70%`로 준다.
