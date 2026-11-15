# 일러스트 샷 리스트 (실행 v1)

작성: illustration-artist / 작성일 2026-10-22 / 입력: `02_writer_figure_plan.md`(C절·시각 메모), `02_writer_draft_r0.md`(1.1.1·2.2.2·3.1.1·3.3.1), `02_writer_numbers.md` 0절, `.claude/skills/bizplan-orchestrator/references/visual-system.md`
생성 도구: gpt-image2 스킬 표준 명령(`uv run .claude/skills/gpt-image2/scripts/generate_image.py`), 모델 gpt-image-2.5-sunburst, 품질 xhigh, 1536x1024, png

## 스타일 바이블 (실제 사용 문단)

모든 신규 생성 프롬프트 맨 앞에 아래 두 문단을 똑같이 붙였다. 첫 문단은 bizplan-illustration 스킬 기본값에 "렌더임을 분명히" 한 줄을 더한 것, 둘째 문단은 세 이미지가 같은 제품으로 보이도록 정한 제품 디자인 고정값이다.

```
Premium stylized 3D render in a clean editorial style for a startup business plan. Soft diffused studio lighting, matte materials, gentle ambient occlusion, subtle depth of field. Clean white to very light cool-grey background with generous negative space. Color palette: deep navy #1B2A4A, cool blue #2E86AB, coral orange #F26B38 used as a single accent, eco green #3BAA6E used sparingly, light grey #E9EDF3. Calm, credible, high-end sportswear mood. No text, no letters, no logos, no brand marks, no watermark, no certification badges. Clearly a rendered concept visualization, not a photograph.

Garment design, identical wherever it appears: a short-sleeve training T-shirt plus training bottoms (men's tapered jogger pants and women's full-length leggings) in a minimal athletic cut. Base fabric is a smooth matte deep navy (#1B2A4A) four-way-stretch knit. Ventilation zones are a visibly open, fine perforated mesh knit in cool blue (#2E86AB): on the T-shirt a vertical panel down the center of the upper back, a side panel under each armpit and a small panel at the center of the chest; on both bottoms a mesh waistband panel across the lower back. Abrasion zones are dense, finely textured reinforced knit panels in slate grey (#8C96A8): across the tops of the T-shirt shoulders, on the knees of both bottoms, and on the seat of the jogger pants. Zones are joined with clean flat bonded seams. The only accent is a slim coral orange (#F26B38) binding around the T-shirt collar.
```

**존 색 규칙(그림 계획 시각 메모와 일치)**
| 존 | 색 토큰 | 원단(본문 표 3-1) | 부위(본문 3.3.1) | 번호 콜아웃 |
|----|--------|-----------------|----------------|-----------|
| 통기·쿨링 존 | SECONDARY #2E86AB | 고통기 메시 | 등 중앙·겨드랑이·허리 뒤·가슴 중앙 | ① |
| 기본 존 | PRIMARY #1B2A4A | 고신축 기본 | 나머지 몸판 | ② |
| 내구 존 | NEUTRAL #8C96A8 | 내구 보강 | 어깨·무릎·엉덩이 | ③ |

- ACCENT(#F26B38)는 우리 제품의 표식 하나(티셔츠 목 둘레 바인딩)에만 썼다. 바디맵(illust-zone-mapping)은 존 색 범례와 혼동되지 않도록 ACCENT를 빼고 존 3색만 썼다.
- 이미지 안 글자는 없다. 숫자 1·2·3이 든 원형 콜아웃만 product-kv와 zone-mapping에 쓰고, 두 그림에서 번호의 뜻(①통기 메시 ②고신축 기본 ③내구 보강)을 똑같이 맞췄다. 뜻은 캡션에 적는다.
- 렌더 스타일을 쓴 이유: 시제품이 아직 없으므로(본문 3.1.1) 실물 사진처럼 보이면 평가위원이 시제품 보유로 오해할 수 있다.

## 샷 선정 결과

| 그림 ID | 결정 | 연결 주장(소목차) | 사유 |
|---------|------|-----------------|------|
| illust-product-kv | 제작 | 1.1.1 "땀·마찰 부위별로 원단을 달리 배치하는 트레이닝웨어" | 이미지 테스트 3문항 모두 예. 상·하의 2종(하의 2핏)의 형태와 존 위치는 글·표로 전달하기 어렵고, 1.1.1의 제품 정의와 1:1로 연결되며, 다른 도해·차트에 제품 형태를 보여 주는 그림이 없다 |
| illust-persona-scene | 제작 | 2.2.2 "1차 타깃은 주 4회 이상 훈련하는 20대 체육 전공자" | 예·예·예. 표 2-3의 페르소나를 실제 사용 맥락(훈련 직후, 땀이 먼저 차는 등·겨드랑이)으로 구체화한다. chart-cohort-performance(수치)와 내용이 겹치지 않고 보완한다 |
| illust-zone-mapping | 제작 | 3.3.1 "'어디에 어떤 원단을 둘지'는 우리가 만듦" | 예·예·예. 인체 전면·후면의 부위별 원단 배치(공간 정보)는 mermaid로 표현하기 어렵다. diagram-problem-tree의 원인 "단일 원단 통짜 패턴"을 해결 쪽에서 시각화하되 같은 내용을 반복하지 않는다(문제 도해는 원인 구조, 이 그림은 설계 결과) |
| illust-fabric-structure | **제외** | (3.1.1 선택 항목) | ① **주장 불일치**: 3.1.1의 주장은 "완료된 것은 사업 모델 설계와 시험 항목 정의이며 원단·시제품·시험은 모두 계획"인데, 흡한속건 원단 단면 개념도는 이 주장을 뒷받침하지 않는다(이미지 테스트 2번 실패). ② **정직성 위험**: 모세관 흡한 구조는 원단 공급사의 일반 기술이다. 본문이 "원단은 사온다"(3.3.1)고 밝히고 심사 예상 질문이 "공급사 기술을 자사 기술처럼 쓰지 않는가"인데, 원단 단면 그림을 넣으면 바로 그 오해를 키운다. ③ **zone-mapping과 중복**: 바디맵 범례가 이미 원단 3종(메시·고신축·내구)의 질감을 보여 주므로 원단 정보가 겹친다(이미지 테스트 3번 실패). ④ 그림 계획상 본문에 자리 표시가 없고 2·3장 쪽수가 빠듯하다 |

## 샷별 기록

### illust-product-kv (채택: `illust_product-kv_v1.png`)
- 목적: 1.1.1에서 "어떤 제품인가"를 한눈에. 반팔 티(후면)·남성 조거(전면 3/4)·여성 레깅스(후면 3/4)를 고스트 마네킹으로 나란히 놓고, 통기 메시·기본·내구 존을 번호 콜아웃 ①②③으로 짚는다.
- 프롬프트 전문: [스타일 바이블 두 문단] +
```
Shot: product concept key visual. The three garments are shown on invisible ghost mannequins (hollow garment shape, no body, no head, no hanger), floating side by side on a seamless white studio background with soft contact shadows. Composition, landscape, eye-level, 85 mm lens look: center and slightly larger, the T-shirt in a back three-quarter view so the cool blue mesh panel down the upper back, the underarm mesh panel and the grey shoulder panels are clearly visible; left, the men's jogger pants in a front three-quarter view showing the grey reinforced knee panels; right, the women's leggings in a back three-quarter view showing the cool blue mesh waistband at the lower back and the grey reinforced knee panels. The garments fill about 70 percent of the frame. Crisp fabric detail so the open mesh perforations, the smooth navy stretch knit and the dense grey reinforced knit are clearly distinguishable. Callouts: exactly three small white circular markers with a thin deep navy outline, each holding one deep navy numeral, connected to the garment by a hairline deep navy leader line: marker 1 points to the blue mesh panel on the T-shirt upper back, marker 2 points to the smooth navy base fabric on the T-shirt sleeve, marker 3 points to the grey knee panel of the jogger pants. The numerals 1, 2 and 3 are the only characters in the image: no words, no labels, no hangtags, no size tags, no logos, no brand name, no human skin, no face.
```
- 설정: `[settings] model=gpt-image-2.5-sunburst quality=xhigh size=1536x1024 format=png`
- 비용: `[usage] 입력 텍스트 671 · 입력 이미지 0 · 출력 2459 토큰 ≈ $0.077`
- 검수 결과(2배 확대 크롭 포함): 통과
  - [x] 핵심 디테일: 등 중앙 메시 패널·겨드랑이 메시·어깨 내구 패널·조거 무릎 내구 패널·레깅스 허리 뒤 메시 밴드·레깅스 무릎 패널이 모두 보이고, 메시 타공·평직 니트·내구 조직의 질감 차이가 확대해도 구분된다
  - [x] 글자·로고·워터마크·인증 마크 없음. 숫자는 1·2·3 각 한 번씩, 지시선 끝점이 각각 등 메시·소매 기본 원단·조거 무릎 패널에 정확히 닿는다
  - [x] 옷 구조 왜곡 없음(조거 끈·주머니·밑단 정상)
  - [x] 팔레트 준수(네이비·쿨블루·슬레이트 그레이, 코럴은 목 둘레 바인딩 한 곳)
- 재시도: 없음(1회 생성 채택)
- 조립 참고: 그림 계획 폭 85%. 캡션에 ①②③ 뜻을 적는다.

### illust-persona-scene (채택: `illust_persona-scene_v1d.png`)
- 목적: 2.2.2의 1차 타깃(20대 체육 전공자)이 셔틀런 훈련 직후 제품을 입은 훈련 현장. 땀이 먼저 차는 등 중앙·겨드랑이의 메시 존이 시선의 중심이 되도록 후면 구도.
- v1 프롬프트 전문: [스타일 바이블 두 문단] +
```
Shot: training-ground usage scene. A bright, minimal indoor training gym with a light natural-wood sports floor, plain light cool-grey walls and tall windows letting in soft morning light that creates gentle rim light and a slight haze; the space is airy and uncluttered. Two athletes in their early twenties, sport majors, have just finished a high-intensity shuttle-run drill. Foreground right: a young man seen from behind, bent forward with hands on his knees catching his breath, a light sheen of sweat on his neck and forearms; the cool blue mesh panel down the back of his T-shirt, the grey shoulder panels and the blue mesh waistband of his navy jogger pants are clearly visible. Mid-ground left: a young woman in side profile turned mostly away from the camera, her face hidden by the backlight and her raised arm as she drinks from a plain matte white water bottle; she wears the same T-shirt and the navy leggings with grey knee panels. Far background, soft focus: a third athlete walking back to the start line. A few plain white training cones and a light grey agility ladder lie on the floor. Plain unbranded light grey training shoes. Characters are semi-realistic stylized 3D figures with natural anatomy and correct hands; no frontal faces, no identifiable faces. Eye-level camera, 35 mm lens look, shallow depth of field, landscape composition. Coral orange appears only on the T-shirt collars. No banners, no signage, no emblems, no crests, no wall text, no scoreboard, no numbers, no logos on clothing, shoes or bottles.
```
- v1b 프롬프트 전문(신규 생성): [스타일 바이블 두 문단] +
```
Shot: training-ground usage scene, rendered as a polished stylized 3D CGI scene with the look of a high-end 3D apparel presentation render: smooth matte skin without pores, slightly simplified anatomy, clean soft lighting, so it reads clearly as a computer-generated concept image and not as a photograph. Setting: a bright, minimal indoor training gym with a light natural-wood sports floor, plain light cool-grey walls and tall windows letting in soft morning light that creates gentle rim light; airy and uncluttered. Moment: sport majors in their early twenties have just finished a shuttle-run drill and are recovering. Foreground right, framed from the head down to mid-thigh: a young man standing upright in a back three-quarter view, hands on his hips, head slightly lowered, catching his breath, a light sheen of sweat on his neck and forearms; the cool blue mesh panel down the upper back of his T-shirt, the underarm mesh panel and the grey shoulder panels are the clear visual focus of the image. Mid-ground left: a young woman walking in side profile, turned partly away from the camera, her face hidden by the backlight and by the plain matte white water bottle she is drinking from; she wears the same T-shirt and the navy leggings with grey knee panels. Background, soft focus: a third athlete wearing the same navy T-shirt and navy jogger pants walking back to the start line between a few plain white training cones; a light grey agility ladder lies on the floor. Plain unbranded light grey training shoes. Camera at shoulder height, 50 mm lens look, shallow depth of field, landscape composition; the framing emphasizes upper bodies and backs, not hips. Natural, modest athletic poses, nobody bending over. No frontal faces, no identifiable faces. Coral orange appears only on the T-shirt collars. No banners, no signage, no emblems, no crests, no wall text, no scoreboard, no numbers, no logos on clothing, shoes or bottles.
```
- v1c 프롬프트 전문(v1b 체이닝 편집, `--input illust_persona-scene_v1b.png`):
```
Edit the reference image. Keep exactly as they are: the composition and framing, the three athletes with their poses and positions, the garments with all their colored zones (deep navy base, cool blue mesh panels, slate grey shoulder and knee panels, thin coral orange collar), the bright gym setting, the white cones, the agility ladder and the window light. Change only the rendering style: re-render the entire image as a polished stylized 3D CGI concept render with the clean matte look of a premium 3D apparel visualization: smooth matte skin without pores or fine skin texture, sculpted and simplified hair shapes, slightly simplified anatomy, soft even global illumination, a slightly lighter and cleaner palette with light cool-grey walls, so the image reads unmistakably as a computer-generated render and not as a photograph. Faces stay hidden or turned away exactly as now. No text, no letters, no numbers, no logos anywhere.
```
- v1d 프롬프트 전문(v1c 체이닝 편집, `--input illust_persona-scene_v1c.png`):
```
Edit the reference image. Keep everything exactly as it is: the stylized 3D CGI render style, the composition, the three athletes and their poses, the garments and all their colored zones, the gym setting, the lighting and the colors. Add only one thing: a subtle, stylized sheen of sweat on the back of the foreground man's neck, his forearms and upper arms, with a few tiny clean droplets near his hairline, and a faint sheen on the woman's neck and arms, rendered in the same smooth CGI style, so it is clear they have just finished an intense drill. Do not add sweat stains on the clothing. No text, no letters, no numbers, no logos anywhere.
```
- 설정: 4회 모두 `[settings] model=gpt-image-2.5-sunburst quality=xhigh size=1536x1024 format=png`
- 비용:
  - v1 `[usage] 입력 텍스트 681 · 입력 이미지 0 · 출력 2459 토큰 ≈ $0.077`
  - v1b `[usage] 입력 텍스트 761 · 입력 이미지 0 · 출력 2459 토큰 ≈ $0.078`
  - v1c `[usage] 입력 텍스트 201 · 입력 이미지 1536 · 출력 2459 토큰 ≈ $0.087`
  - v1d `[usage] 입력 텍스트 159 · 입력 이미지 1536 · 출력 2459 토큰 ≈ $0.087`
- 검수 결과
  - v1 (폐기): 화면 중앙 전경이 허리를 숙인 남성의 엉덩이(그레이 내구 패널)여서 시선이 등 메시 존이 아니라 둔부로 간다. 사업계획서 그림으로 어색하고 주장(등·겨드랑이 통기)과 초점이 어긋남. 배경 인물이 반바지를 입어 제품 일관성도 깨짐
  - v1b (폐기): 구도 해결(상체·등 메시 존이 초점, 세 인물 모두 제품 착용). 그러나 피부·머리카락 질감이 실사 사진 수준이라 "실제 착용 사진·실존 인물"로 오해될 위험이 있고, 다른 두 샷(3D 렌더)보다 스타일이 튐
  - v1c (폐기): 구도·의상을 유지한 채 매끈한 CGI 렌더 스타일로 바뀌어 컨셉 이미지임이 분명해지고 다른 샷과 톤이 맞음. 다만 스타일 변환 과정에서 땀 표현이 사라져 "고강도 훈련 직후" 맥락이 약해짐
  - v1d (채택): v1c에 목·팔의 땀 광택과 작은 물방울만 더함. 체크리스트 통과
    - [x] 핵심 디테일: 전경 남성의 등 중앙 메시·겨드랑이 메시·어깨 내구 패널·코럴 목 바인딩, 여성의 레깅스 무릎 패널, 배경 인물의 조거 엉덩이·무릎 패널이 모두 제품 디자인과 일치
    - [x] 글자·로고·현수막·엠블럼·학교명·점수판 없음. 물병·신발·콘 무지
    - [x] 얼굴: 남성은 고개 숙인 후면, 여성은 물병에 가린 측면, 배경 인물은 후면 — 특정 불가. 손(허리 짚은 두 손, 물병 쥔 손) 왜곡 없음(2배 확대 확인)
    - [x] 스타일: 매끈한 CGI 렌더, 밝은 쿨그레이 실내, 팔레트 준수(코럴은 목 바인딩만)
- 재시도: 3회(구도 1회 → 렌더 스타일 일관성 1회 → 땀 디테일 보강 1회). 사유는 위 검수 결과
- 조립 참고: 그림 계획 폭 70%. 캡션에 "가상 인물" 명시

### illust-zone-mapping (채택: `illust_zone-mapping_v1b.png`)
- 목적: 3.3.1의 핵심 기술 ① 존 매핑 설계를 바디맵으로. 왼쪽에 흐릿한 "단일 원단 통짜 패턴" 마네킹 → 오른쪽에 전면·후면 존 매핑 마네킹을 두어 기존 방식과의 차이를 보이고, 아래에 원단 3종 견본 범례(①②③)를 둔다. 수치·규격·시험 결과는 넣지 않음(결과가 없기 때문).
- v1 프롬프트 전문: [스타일 바이블 두 문단] +
```
Shot: technical body-zone map concept, like a clean design blueprint rendered in 3D on a white background. Main subject: two identical gender-neutral mannequin figures with smooth matte light-grey bodies and featureless heads (no face, no hair), standing in a relaxed A-pose, full body, wearing the T-shirt and jogger pants described above but without the coral collar: the left figure in a straight front view, the right figure in a straight back view, side by side, placed center-right. Front view zones: cool blue mesh at the center chest and under both armpits; slate grey reinforced panels on the shoulder tops and the knees; deep navy base everywhere else. Back view zones: cool blue mesh vertical panel down the upper back, under both armpits and the lower-back waistband; slate grey reinforced panels on the shoulder tops and the seat; deep navy base everywhere else. Zone panels have crisp, clean edges like a technical diagram while the fabric textures stay visible. Contrast element on the far left: a smaller, faded mannequin (about two-thirds the height, low contrast) in the same front pose wearing a conventional training top and pants cut from one single uniform pale grey fabric with no zones, followed by a simple thin light-grey chevron arrow pointing right toward the zoned figures. Legend: along the bottom center, three small round fabric swatch icons evenly spaced in a row: a cool blue open-mesh swatch, a smooth deep navy stretch-knit swatch, and a dense slate grey reinforced-knit swatch; beside each swatch a small white circular marker with a thin deep navy outline holding the deep navy numeral 1, 2 and 3 respectively. The numerals 1, 2 and 3 are the only characters in the image: no words, no measurements, no other numbers, no heat-map gradients, no airflow arrows, no labels, no coral orange anywhere.
```
- v1b 프롬프트 전문(v1 체이닝 편집, `--input illust_zone-mapping_v1.png`):
```
Edit the reference image. Keep everything else exactly as it is: the white background, the overall layout, the thin chevron arrow, the three round fabric swatches with the white numbered markers 1, 2 and 3 along the bottom, the garment colors, the zone positions and fabric textures, the shoes, the lighting and the premium 3D render style. Change only the body form of all three mannequins: make them slimmer, gender-neutral abstract display mannequins with simplified smooth matte light-grey forms, no pronounced muscles, moderate shoulders, a soft neutral torso and smooth egg-shaped featureless heads, so they read as neither male nor female. On the back-view figure, make the slate grey reinforced seat panel smaller and cleaner, following the seam lines so it is less prominent, while staying clearly visible. Do not add any text, letters, labels or extra numbers; the numerals 1, 2 and 3 in the legend markers remain the only characters.
```
- 설정: 2회 모두 `[settings] model=gpt-image-2.5-sunburst quality=xhigh size=1536x1024 format=png`
- 비용:
  - v1 `[usage] 입력 텍스트 743 · 입력 이미지 0 · 출력 2459 토큰 ≈ $0.077`
  - v1b `[usage] 입력 텍스트 215 · 입력 이미지 1536 · 출력 2459 토큰 ≈ $0.087`
- 검수 결과
  - v1 (폐기): 구성·존 위치·범례는 계획대로였으나 마네킹이 근육질 남성 체형이라 그림 계획의 "성별 중립 실루엣"과 다르고, 여성 레깅스 핏이 있는 제품을 남성 전용처럼 보이게 함
  - v1b (채택): 레이아웃·범례·존 위치를 유지하고 마네킹을 더 가늘고 근육 표현이 적은 달걀형 무안면 마네킹으로 바꿈. 체크리스트 통과
    - [x] 핵심 디테일: 전면(가슴 중앙 V형 메시·겨드랑이 메시·어깨/무릎 내구 패널), 후면(등 중앙 메시·겨드랑이 메시·허리 뒤 메시 밴드·어깨/엉덩이 내구 패널), 왼쪽 단일 원단 비교 마네킹과 오른쪽 화살표, 하단 원단 견본 ①②③(2배 확대 확인)
    - [x] 글자·로고·수치·열지도·기류 화살표 없음. 숫자는 범례의 1·2·3만
    - [x] 마네킹·옷 구조 왜곡 없음
    - [x] 팔레트: 존 3색(SECONDARY·PRIMARY·NEUTRAL)만 사용, ACCENT 없음(범례 혼동 방지)
  - 남은 한계: 마네킹 어깨가 아직 다소 넓어 완전한 성별 중립보다는 "표준 디스플레이 마네킹"에 가깝다. 엉덩이 내구 패널 크기는 거의 줄지 않았으나 부위 표시로는 적절해 수용함
- 재시도: 1회(체형 보정 체이닝 편집)

## 일관성 점검 (최종 3장 나란히 비교)
- 같은 제품으로 보이는가: 세 그림 모두 네이비 몸판 + 등 중앙 세로 메시(쿨블루) + 겨드랑이 메시 + 어깨 그레이 내구 패널 + 무릎 그레이 패널로 같은 디자인. product-kv와 persona-scene은 코럴 목 바인딩까지 같음
- 같은 시각 언어인가: 모두 3D 렌더, 흰색~밝은 쿨그레이 배경, 부드러운 확산광, 매트 재질. 실사 사진처럼 보이던 persona-scene v1b를 v1c·v1d에서 렌더 스타일로 맞춰 해결
- 번호 체계: product-kv의 ①②③과 zone-mapping 범례의 ①②③이 같은 뜻(통기 메시·고신축 기본·내구 보강)
- 결과: 스타일이 튀는 샷 없음. 추가 재생성 불필요

## 폐기 파일 (자산 목록 미등록, 조립 시 사용 금지)
- `output/01_사업계획서_초안/assets/illustrations/illust_persona-scene_v1.png`, `_v1b.png`, `_v1c.png`
- `output/01_사업계획서_초안/assets/illustrations/illust_zone-mapping_v1.png`

## 비용 합계 ([usage] 추정치 기준)
| 파일 | 방식 | 추정 비용 |
|------|------|----------|
| illust_product-kv_v1.png (채택) | 생성 | $0.077 |
| illust_zone-mapping_v1.png | 생성 | $0.077 |
| illust_zone-mapping_v1b.png (채택) | 체이닝 편집 | $0.087 |
| illust_persona-scene_v1.png | 생성 | $0.077 |
| illust_persona-scene_v1b.png | 생성 | $0.078 |
| illust_persona-scene_v1c.png | 체이닝 편집 | $0.087 |
| illust_persona-scene_v1d.png (채택) | 체이닝 편집 | $0.087 |
| **합계 (7회 호출)** | | **≈ $0.570** |

- 품질은 전부 xhigh(하향 없음). 디테일 뭉개짐이 없어 max 재생성은 필요하지 않았다.
- 실행 메모: 이 에이전트의 셸 작업 디렉터리가 매 호출 `_workspace/v1`로 초기화되므로, 표준 명령 앞에 `cd <프로젝트 루트> &&`를 붙여 프로젝트 루트에서 실행했다(명령 문자열 자체는 2절 표준 형태 그대로).
