# 사업계획서 시각 시스템 — 차트·도해·일러스트 공통 기준

차트(data-analyst), 도해(diagram-designer), 일러스트(illustration-artist)를 서로 다른 에이전트가 만들어도 한 문서처럼 보이게 하는 공통 기준이다. 문서 한 권에서 색과 글꼴이 그림마다 다르면 평가위원은 내용보다 이음매를 먼저 본다.

## 1. 색상

| 토큰 | HEX | 의미·용도 |
|------|-----|----------|
| PRIMARY | `#1B2A4A` | 딥 네이비. 제목, 주요 노드 테두리, 기본 막대 |
| SECONDARY | `#2E86AB` | 쿨 블루. 기능성(쿨링·통기)·보조 계열 |
| ACCENT | `#F26B38` | 코럴 오렌지. **우리 회사·우리 제품·핵심 강조에만** 쓴다 |
| ECO | `#3BAA6E` | 그린. 친환경·ESG·리사이클 |
| NEUTRAL | `#8C96A8` | 경쟁사·비교 대상·보조선 |
| LIGHT | `#E9EDF3` | 배경 면, 노드 채움 |
| WARN | `#C8553D` | 문제·Pain Point·리스크 |

- 한 그림에서 ACCENT는 한 대상에만 쓴다. 강조가 여러 곳이면 아무것도 강조되지 않는다.
- 경쟁사는 모두 NEUTRAL 계열(명도 차이)로 칠하고 브랜드 고유색을 쓰지 않는다. 특정 경쟁사를 돋보이게 하거나 깎아내리는 인상을 피하기 위해서다.
- 배경은 흰색. 인쇄(흑백 복사 포함)에서도 구분되도록 색만으로 의미를 전달하지 않고 레이블·패턴을 함께 쓴다.

## 2. 글꼴

- 우선순위: Pretendard → Apple SD Gothic Neo → Noto Sans KR → NanumGothic → Malgun Gothic
- 차트 제목 14~16pt Bold, 축·레이블 10~11pt, 출처 8~9pt
- 도해 노드 글자는 한 줄 12자 안팎, 두 줄까지

## 3. 그림 ID와 파일 이름

| 유형 | 그림 ID 형식 | 파일 |
|------|-------------|------|
| 데이터 차트 | `chart-{slug}` | `{OUT}/assets/charts/chart_{slug}_v{N}.png` |
| mermaid 도해 | `diagram-{slug}` | `{OUT}/assets/diagrams/diagram_{slug}_v{N}.mmd`, `.png` |
| AI 일러스트 | `illust-{slug}` | `{OUT}/assets/illustrations/illust_{slug}_v{N}.png` |

- slug는 영문 소문자·숫자·하이픈 (예: `market-growth`, `supply-chain`)
- 파일 이름의 `_v{N}`은 그 파일을 만든 실행 버전이다. 같은 이름이 있으면 덮어쓰지 않고 실행 버전을 올리거나 `_v{N}b`처럼 구분한다.

## 4. 자산 목록(JSON) 형식

각 제작 에이전트는 자기 자산 목록을 `{WS}/{단계}_{에이전트}_assets.json`에 쓴다. 조립 스크립트가 모든 `*_assets.json`을 합쳐 본문의 `{{FIG:그림ID}}`를 그림으로 바꾼다.

```json
[
  {
    "id": "chart-market-growth",
    "type": "chart",
    "path": "output/01_사업계획서_초안/assets/charts/chart_market-growth_v1.png",
    "caption": "국내 애슬레저 시장은 2018~2024년 연평균 21% 성장",
    "source": "athleisure_market_data.csv(출처 미기재 데이터, 원출처 확인 필요)",
    "width": "85%"
  }
]
```

- `path`는 프로젝트 루트 기준 상대 경로
- `caption`은 결론형 한 문장(그림 번호는 조립 스크립트가 붙인다)
- `source`는 데이터·내용의 출처. AI 일러스트는 `"AI 생성 컨셉 이미지(실제 제품 아님)"`
- `width`는 문서 폭 대비 비율(선택, 기본 90%)
