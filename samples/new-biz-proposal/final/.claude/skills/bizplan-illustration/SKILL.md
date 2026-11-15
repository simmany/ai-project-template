---
name: bizplan-illustration
description: "사업계획서·IR 자료에 넣을 AI 일러스트의 아트 디렉션 기준. 설득에 필요한 샷만 고르는 기준, 문서 전체의 스타일 통일(스타일 바이블), 정직성 규칙(컨셉 이미지 표시, 가짜 인증·로고·실존 인물 금지), 프롬프트 구성, 검수와 재생성, 캡션·자산 목록 작성을 다룬다. 생성 실행은 gpt-image2 스킬을 쓴다. 사업계획서 일러스트, 제품 컨셉 이미지, 키비주얼, 소재 개념도 일러스트, 사용 장면 이미지 요청이나 illustration-artist 에이전트 작업에 사용한다. 도해·흐름도는 mermaid-diagram, 데이터 차트는 data-file-analysis를 쓴다."
---

# 사업계획서 일러스트 아트 디렉션

사업계획서의 이미지는 장식이 아니다. 평가위원이 글보다 빨리 이해해야 하는 것(제품의 형태, 소재 구조, 사용 맥락)을 보여 줄 때만 넣는다. 이미지가 많다고 점수가 오르지 않고, 내용 없는 이미지는 오히려 분량만 차지한다.

실행 명령·파라미터·비용·트러블슈팅은 `gpt-image2` 스킬을 따른다. 이 스킬은 "무엇을, 어떤 기준으로 그릴지"를 정한다.

## 1. 샷 선정 — 이미지 테스트

그림 계획의 `illustration` 항목마다 세 질문에 모두 "예"일 때만 만든다.

1. 글이나 도해로는 전달하기 어려운 것(형태·질감·공간·사용 장면)을 보여 주는가?
2. 특정 소목차의 특정 주장 하나와 직접 연결되는가?
3. 다른 도해·차트와 같은 내용을 반복하지 않는가?

| 샷 유형 | 설득 효과 | 추천 위치 | 주의 |
|--------|----------|----------|------|
| 제품 컨셉 키비주얼 | 아이템을 한눈에 이해 | 1.1.1 | 실제 시제품 사진처럼 보이지 않게(렌더 스타일) |
| 소재·구조 개념도(단면·바디맵) | 기술 차별점을 직관적으로 | 3.3.1, 3.1.1 | 시험 수치·인증 마크를 그리지 않음 |
| 타깃 사용 장면 | 페르소나·구매 상황의 현실감 | 2.2.2, 4.2.1 | 실존 인물·후기처럼 보이지 않게 |
| 공급망·순환 일러스트 | ESG·지역 협력을 감성적으로 | 5.3.1 | 같은 흐름의 mermaid 도해가 있으면 생략 |

권장 3~5장. 뺀 항목은 샷 리스트에 사유를 적는다.

## 2. 스타일 바이블 — 모든 프롬프트의 공통 머리말

모든 샷이 한 문서에 속해 보이도록 스타일 문단 하나를 먼저 정하고 모든 프롬프트 앞에 똑같이 붙인다. 그림 계획의 "시각 메모"(브랜드 키워드·톤)와 `.claude/skills/bizplan-orchestrator/references/visual-system.md` 팔레트를 반영한다.

기본값(특별한 이유가 없으면 이것을 쓴다):

```
Premium stylized 3D render in a clean editorial style for a startup business plan.
Soft diffused studio lighting, matte materials, gentle ambient occlusion, subtle depth of field.
Clean white to very light cool-grey background with generous negative space.
Color palette: deep navy #1B2A4A, cool blue #2E86AB, coral orange #F26B38 used as a single accent,
eco green #3BAA6E used sparingly, light grey #E9EDF3. Calm, credible, high-end sportswear mood.
No text, no letters, no logos, no brand marks, no watermark, no certification badges.
```

- 스타일을 샷마다 바꾸지 않는다. 사실적 사진 스타일과 플랫 일러스트를 섞으면 문서가 조각나 보인다.
- 렌더 스타일(사진이 아님)을 쓰는 이유: 존재하지 않는 시제품을 사진처럼 보이게 하면 평가위원이 실물이 있다고 오해할 수 있다.

## 3. 정직성 규칙

- 실제 브랜드 로고·상징, 실존 인물, 유명인 닮은 얼굴을 넣지 않는다.
- 인증 마크(GRS 등), 시험 수치, 별점, 후기 말풍선을 그리지 않는다. 근거처럼 보이는 가짜 요소는 문서 전체의 신뢰를 깎는다.
- 이미지 안 글자는 원칙적으로 넣지 않는다. 구역을 가리켜야 하면 숫자(1, 2, 3)가 든 원형 콜아웃만 쓰고 뜻은 캡션에 적는다. 한글 글자는 철자 오류 위험이 커서 쓰지 않는다.
- 모든 캡션에 출처로 `AI 생성 컨셉 이미지(실제 제품 아님)`를 적는다.

## 4. 프롬프트 구성

`[스타일 바이블] + [피사체] + [구도·카메라] + [주장과 연결된 핵심 디테일] + [배제 조건]` 순서로 쓴다. gpt-image 계열은 문장을 그대로 반영하므로 구체적으로 쓴다.

| 요소 | 좋은 예 |
|------|--------|
| 피사체 | "a women's running training set (cropped long-sleeve top and leggings) on an invisible mannequin" |
| 구도 | "three-quarter front view, centered, garment fills 60% of frame, landscape composition" |
| 핵심 디테일 | "breathable laser-perforated mesh zones on upper back and underarms tinted cool blue; dense compression zones on thighs in navy; one coral accent seam line" |
| 배제 | "no text, no logo, no human face" |

- 핵심 디테일은 본문의 주장(예: 부위별 통기 설계)을 그대로 시각화한다. 본문에 없는 기능을 그리지 않는다.
- 사람이 나오는 장면은 얼굴이 작거나 뒷모습·측면이 되게 구성한다(실존 인물 오해 방지, 렌더 품질 안정).

## 5. 생성 설정

- 모델은 gpt-image2 스킬 기본값(sunburst). 품질은 문서 납품용이므로 `--quality xhigh`.
- 크기: 본문 폭 가로형 `1536x1024`. 세로로 긴 피사체만 `1024x1536`.
- 출력: `{OUT}/assets/illustrations/illust_{slug}_v{N}.png`
- 명령은 gpt-image2 스킬 2절의 표준 문자열을 그대로 쓴다(프로젝트 루트에서, `cd` 없이). Bash `timeout`은 600000.
- 서로 독립인 샷은 한 메시지에서 최대 3개까지 병렬로 실행할 수 있다. 429(속도 제한)가 나면 순차 실행으로 바꾼다.
- 각 실행의 stderr `[settings]`·`[usage]`를 샷 리스트에 기록한다.

## 6. 검수와 재생성

생성 직후 Read로 이미지를 직접 본다.

- [ ] 핵심 디테일(주장과 연결된 요소)이 보인다
- [ ] 글자·로고·워터마크·인증 마크가 없다(숫자 콜아웃 제외)
- [ ] 손·얼굴·옷 구조의 왜곡이 없다
- [ ] 스타일 바이블과 팔레트를 따른다

미흡하면 프롬프트를 고쳐 같은 설정으로 한 번 더 생성한다(파일명 `_v{N}b`). 디테일이 뭉개졌으면 `--quality max`로 올린다. 그래도 미흡하면 가장 나은 결과를 쓰고 미흡점을 샷 리스트에 적는다.

**일관성 점검:** 모든 샷을 만든 뒤 함께 보고, 스타일이 튀는 샷은 가장 잘 나온 샷을 `--input` 레퍼런스로 넘겨 "Match the rendering style, lighting and color palette of the reference image" 지시로 다시 생성한다.

## 7. 산출물

1. `{WS}/03_illustration-artist_shotlist.md`

```markdown
# 일러스트 샷 리스트 (실행 v{N})
## 스타일 바이블 (실제 사용 문단)
## 샷 선정 결과
| 그림 ID | 결정(제작/제외) | 연결 주장(소목차) | 사유 |
## 샷별 기록
### illust-{slug}
- 목적 / 프롬프트 전문 / 설정([settings]) / 비용([usage]) / 검수 결과 / 재시도
## 비용 합계
```

2. `{WS}/03_illustration-artist_assets.json` — `visual-system.md` 4절 형식. `caption`은 "무엇을 보여 주는지" 한 문장(예: "부위별 통기·압박 존을 나눈 바디맵 설계 컨셉"), `source`는 `AI 생성 컨셉 이미지(실제 제품 아님)`.
