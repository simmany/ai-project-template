---
name: gpt-image2
description: "OpenAI ChatGPT Images 2.5 (GPT Image 2.5) 이미지 생성/편집 스킬. 기본 모델은 최고 성능인 gpt-image-2.5-sunburst이고 품질은 high 이상(high·xhigh·max)만 쓴다. 사용자가 속도를 우선할 때만 gpt-image-2.5-flare, 구세대 gpt-image-2 호환. 텍스트→이미지, 이미지 편집(마스킹), 멀티 이미지 합성, 멀티턴 체이닝 편집(방금 만든 이미지 이어서 수정·다시 생성)을 수행. 사용자의 자연어 요청만으로 명령 구성→실행→결과 검증→보고까지 이 스킬이 수행한다. 사용 시점: OpenAI/ChatGPT 이미지 생성, AI 이미지 생성(특히 텍스트 렌더링 품질이 중요하거나 2K 이상 해상도·사실적 사진·인포그래픽·로고·제품 목업·마스킹 편집·멀티 레퍼런스 합성이 필요할 때), GPT Image, DALL-E 후속 모델, ChatGPT Images 2.5/2.0 언급 시. Gemini·Nano Banana 요청이나 차트·다이어그램을 코드로 그리는 작업에는 사용하지 않는다."
allowed-tools:
  - "Bash(uv run .claude/skills/gpt-image2/scripts/generate_image.py:*)"
  - "Bash(uv run .claude/skills/gpt-image2/scripts/make_mask.py:*)"
---

<!-- 버전 v0.4 (2026-09-28) | 품질 우선 정책: 기본 모델 flare → sunburst(OpenAI 문서상 "the most capable model"),
     quality 하한 high(high·xhigh·max만 허용, 스크립트가 low·medium·auto 거부), API 키는 환경변수 → .env(현재 디렉터리 → 프로젝트 루트)만 사용
     (~/.config/openai/.env 폴백 제거), openai>=3.10 하한(uv 캐시에 openai 2.52~3.8 구버전 환경이 남아 있었음),
     사용 토큰·추정 비용 출력. 근거: developers.openai.com/api/docs/models/gpt-image-2.5-sunburst · changelog (2026-09-28 확인),
     openai-python v3.10.0 "add GPT Image 2.5 models and image options".
     버전 v0.3 (2026-09-11, REQ-002 적용) | ChatGPT Images 2.5 대응: 기본 모델 gpt-image-2.5-flare, --model 선택(sunburst/gpt-image-2),
     quality xhigh·max, background transparent 지원, --input-fidelity 옵션, OPENAI_API_KEY .env 폴백.
     근거: developers.openai.com/api/docs/models/gpt-image-2.5-flare · gpt-image-2.5-sunburst · guides/image-generation (2026-09 확인),
     openai.com/index/introducing-chatgpt-images-2-5 (2026-09-08 출시).
     버전 v0.2 (2026-08-04, REQ-003 적용) | 원본: 외부 작성 스킬 (버전 표기 없음, API 문서 2026-04 기준)
     변경: pip 전역 설치(--break-system-packages) 폐지 → uv 격리 실행(PEP 723 인라인 의존성),
     자연어 단독 운용을 위한 실행 런북으로 전면 개편, scripts/make_mask.py 신규,
     인라인 API 예제는 references/api_reference.md로 이동.
     설계 근거: output/03.GPT Image2 스킬 개선 검토/GPT_Image2_스킬_개선_설계_v0.2.md -->

# OpenAI ChatGPT Images 2.5 (GPT Image 2.5) — 실행 런북

## 1. 역할

이 문서의 독자는 Claude다. 사용자는 **자연어로만** 요청한다 — 명령어·파라미터·파일 검수를 기대하지 않는다. 아래 규칙에 따라 명령 구성 → 실행 → 검증 → 보고를 수행한다.

모델은 **ChatGPT Images 2.5 계열** (2026-09-08 출시, 2026-09-28 기준 최신). 이 스킬은 **품질 우선**이다.

- 기본 **`gpt-image-2.5-sunburst`** — OpenAI 문서상 "the most capable model for image generation and editing". 생성 시간은 더 길지만 세밀한 디테일·편집 정밀도·레퍼런스 보존이 가장 좋다.
- **`gpt-image-2.5-flare`** — 빠른 일상 생성용(지연 약 50% 감소). 사용자가 "빨리", "속도 우선"처럼 **속도를 명시했을 때만** 쓴다.
- `gpt-image-2` — 구세대 호환이 필요할 때만. quality 상한이 `high`라 스크립트가 xhigh·max를 high로 낮춘다.

두 2.5 모델의 토큰 단가는 같으므로 모델 선택은 비용이 아니라 속도와 품질로 정한다. 모델 요점: 한 변 최대 3840px(2560x1440 초과는 실험적), 편집 시 레퍼런스 피사체·조명·질감 보존력 향상, 요청한 부분만 바꾸는 편집 정밀도, `quality`에 **`xhigh`·`max`** 추가, `background="transparent"` 지원(png·webp).

## 2. 실행 환경

이 스킬은 `uv`로 격리된 Python 환경에서 실행한다. 스크립트에 선언된 PEP 723 인라인 의존성을 `uv`가 자동 준비하므로 **별도 설치 단계가 없다** (첫 실행만 환경 구성으로 몇 초 소요, 이후 캐시).

필수 조건:

- 시스템에 `uv`가 설치되어 있어야 한다. 없으면: `curl -LsSf https://astral.sh/uv/install.sh | sh` 또는 `brew install uv`
- `OPENAI_API_KEY`는 **환경변수를 먼저** 쓰고, 없으면 **`.env` 파일**(현재 디렉터리 → 프로젝트 루트 순)에서 스크립트가 읽는다 (`OPENAI_API_KEY=sk-...` 한 줄, v0.4). 그 밖의 위치는 읽지 않는다. 13절 사용자 준비 참조
- 전역 Python에 패키지를 설치하지 않는다. `pip`, `pip3`, `--break-system-packages`를 사용하지 않는다
- API 키의 값을 명령 출력이나 응답에 노출하지 않는다. 키 존재 확인은 스크립트의 종료 코드 2 메시지로만 판단한다 — `env`·`printenv`·`echo $OPENAI_API_KEY` 금지

**표준 명령** — 프로젝트 루트 기준으로 아래 문자열 형태를 그대로 사용한다 (`cd` 금지, 경로에 따옴표 불필요 — allowed-tools 규칙과 리터럴 매칭):

```bash
uv run .claude/skills/gpt-image2/scripts/generate_image.py "<프롬프트>" [옵션]
uv run .claude/skills/gpt-image2/scripts/make_mask.py --base <원본> [영역 옵션]
```

generate_image.py 주요 옵션: `--model`(sunburst 기본 / flare / gpt-image-2) `--size` `--quality`(**high 기본**·xhigh·max — low·medium·auto는 거부) `--background`(auto·opaque·transparent) `--input-fidelity`(high·low, gpt-image-2 편집 전용) `--n` `--output`(-o, 미지정 시 `generated_images/`) `--format`(미지정 시 `--output` 확장자로 추론) `--compression` `--moderation` `--input`(-i, 여러 개 가능) `--mask` `--force`

스크립트는 stderr에 `[settings]`(실제 적용한 model·quality·size·format)와 `[usage]`(토큰 사용량·추정 비용)를 출력한다. 보고할 때 이 값을 그대로 쓴다.

종료 코드: 0 성공 / 1 API·처리 실패 / 2 사용 오류 (키 없음 · 인자 오류 · 입력 파일 없음 · 형식 불일치 · 덮어쓰기 거부). 사용 오류는 API 호출 전에 걸러지므로 비용이 들지 않는다.

## 3. 요청 해석 → 실행 결정표

모델은 모든 모드에서 기본 sunburst다(`--model` 생략). 사용자가 속도를 명시했을 때만 `--model gpt-image-2.5-flare`를 붙인다.

| 요청 신호 (예) | 모드 | 명령 골격 |
|---------------|------|----------|
| "~만들어줘/그려줘" — 입력 이미지 없음 | 생성 | `generate_image.py "<프롬프트>"` |
| "이 파일/사진을 바꿔줘" — 전반 수정 | 편집 | `--input <파일>` |
| "~만 바꿔줘" — 의미 영역 (배경만, 옷 색만) | 편집 (prompt-only 우선) | `--input <파일>` + 프롬프트에 유지 대상 명시 |
| "오른쪽 절반에/이 좌표에" — 위치·구역 지정 | 마스킹 편집 (7절) | `make_mask.py` → `--input <파일> --mask <마스크>` |
| "이 사진들을 합쳐서/함께" | 멀티 레퍼런스 합성 | `--input a.png b.png c.png` (최대 10장, 각 20MB) |
| "방금/아까 그 이미지에서 이어서" | 체이닝 편집 (8절) | `--input <직전 출력 파일>` (직전과 같은 model·quality) |
| "여러 안/시안 보여줘" | 생성 n>1 | `--n 3` (quality high 유지 — 9절 비용 규칙 적용) |
| "투명 배경/누끼" | 생성·편집 | `--background transparent` (png·webp) |
| "빨리/대충 빠르게" — 속도 명시 | 생성·편집 | 위 골격 + `--model gpt-image-2.5-flare` (quality는 high 유지) |

스트리밍(`--stream`)은 에이전트 기본 플로우에서 쓰지 않는다 (부분 이미지당 +100토큰, 에이전트는 중간 이미지를 활용할 수 없음).

## 4. 파라미터 추론 규칙

사용자가 지정하지 않은 값은 아래 기준으로 결정한다.

| 파라미터 | 추론 규칙 |
|----------|----------|
| `--size` | 로고·아이콘·프로필 → `1024x1024` / 배너·썸네일·가로 표지 → `1536x1024` / 포스터·세로 홍보물 → `1024x1536` / 인쇄·고해상 언급 → 2048 이상 (한 변 64~3840, 16의 배수, 종횡비 3:1 이내) / 그 외 → `auto` |
| `--quality` | **하한은 `high`** — 시안·초안·"여러 안"·미지정 모두 `high` / "고품질·세밀·인쇄·납품·교재" → `xhigh` / "최고·최상 품질", "max", "비용 무관" → `max`. `low`·`medium`은 쓰지 않는다(스크립트가 거부). 사용자가 저품질을 직접 요청해도 `high`로 진행하고 보고에 그 사실을 적는다 |
| `--format` | 기본 png / "웹용·용량 줄여" → `webp` + `--compression 90` (품질 손실을 줄이기 위해 90 이상) |
| `--n` | 미지정 1 / "여러 안" 3 |

모호성 처리: **실행을 막는 모호성**(어느 파일인지 특정 불가 등)만 질문하되 한 번에 묶어 묻는다. 나머지는 위 기본값으로 진행하고 보고에 "적용한 설정"으로 명시한다.

## 5. 파일 경로 규칙

- **입력**: 사용자가 말한 파일명을 Glob으로 탐색해 확정. 동명 다수·불일치 시 후보를 제시해 확인. "방금 만든 것" = 대화 내 마지막 출력 경로.
- **출력**: 기본 `generated_images/` 하위에 의미 있는 파일명으로 `--output` 지정 (예: `generated_images/logo_morning_brew_v1.png`). 같은 이름이 있으면 `_v2`, `_v3`로 올린다 — 스크립트의 덮어쓰기 가드(exit 2)는 최후 안전망이고, `--force`는 사용자가 덮어쓰기를 명시했을 때만 쓴다.
- 프로젝트 디렉토리 밖에는 쓰지 않는다.

## 6. 실행 후 검증·보고

1. 저장된 이미지를 Read로 열어 직접 확인한다.
2. 대조 3항: (i) 요청의 명시 요소가 모두 있는가 (ii) 텍스트 문구의 철자가 정확한가 — 따옴표로 지정한 문구 우선 (iii) 명백한 왜곡·결함이 없는가.
3. 미충족 시 프롬프트를 보강해 **같은 model·quality로 1회 자동 재시도**한다(재시도 비용이 9절의 고지 기준을 넘으면 먼저 알린다). 디테일이 뭉개졌으면 quality를 한 단계 올려(high→xhigh→max) 재시도한다. 재시도 후에도 미흡하면 결과와 미흡점을 보고하고 사용자 판단에 맡긴다.
4. 보고: 저장 경로 / 적용 설정(stderr `[settings]`의 model·quality·size) / 추정 비용(`[usage]`) / 반영 내용 / 미흡점·재시도 여부 — 간결하게.
5. `--n`>1이면 각 이미지를 확인하고 최적 1장을 추천한다.

## 7. 마스킹 편집 절차

원칙: **prompt-only 편집 우선.** gpt-image-2.5는 기본이 고충실도라 "X만 바꾸고 나머지는 그대로" 지시를 잘 따른다. 마스크는 사용자가 **위치·구역**을 말했을 때만 쓴다 ("오른쪽 절반", "위쪽 30%", "이 좌표"). 객체 인식 기반 정밀 선택("소파만 정확히")은 불가 — prompt-only로 처리하거나 구역을 되물어 기하 마스크로 근사한다.

```bash
# 1) 마스크 생성 — 지정 영역 = 알파 0(재생성), 나머지 = 알파 255(유지), 크기는 --base와 동일
uv run .claude/skills/gpt-image2/scripts/make_mask.py --base room.png --region right --ratio 0.5 --output generated_images/room_mask.png
# 옵션: --rect X0,Y0,X1,Y1 (반복) / --circle CX,CY,R (반복) / --region top|bottom|left|right --ratio / --from-gray 흑백.png / --invert

# 2) 마스킹 편집
uv run .claude/skills/gpt-image2/scripts/generate_image.py "빈 공간에 빨간 소파" --input room.png --mask generated_images/room_mask.png --output generated_images/room_sofa_v1.png
```

마스킹·정밀 편집에는 기본 모델인 sunburst를 그대로 쓴다(flare로 바꾸지 않는다). `--input-fidelity high`는 **구세대 `gpt-image-2` 전용**이다 — 2.5 계열은 이 파라미터를 거부하며(400 `invalid_input_fidelity_model`) 기본이 고충실도이므로 스크립트가 자동으로 무시한다(2026-09-11 실측).

## 8. 이어서 수정 (멀티턴)

직전 출력 파일을 `--input`으로 넘겨 체이닝한다. 매 턴 결과를 6절로 검증하고, 출력은 `_v2`, `_v3`로 올린다.

```bash
uv run .claude/skills/gpt-image2/scripts/generate_image.py "배경을 크림색으로" --input generated_images/logo_v1.png --output generated_images/logo_v2.png
```

Responses API 기반 멀티턴(모델 추론 + `previous_response_id`)은 이 스킬의 기본 플로우가 아니다 — 필요 시 references/api_reference.md 참조.

## 9. 비용 규칙

품질을 낮춰 비용을 줄이지 않는다. 비용은 **장수와 해상도**로 관리하고, 큰 비용은 미리 알린다.

gpt-image-2.5(sunburst·flare)는 gpt-image-2와 **같은 토큰 단가**다(텍스트 입력 $5/M, 이미지 입력 $8/M, 이미지 출력 $30/M 토큰). OpenAI는 2.5의 장당 가격표를 내지 않았고 gpt-image-2 계산기도 2.5의 토큰 사용량을 추정하지 못한다고 밝혔다. 그러므로 **실행 후 stderr `[usage]`의 추정 비용을 기준**으로 삼는다. 첫 실행 전 추정에는 아래 gpt-image-2 `high` 참고치(2026-04)를 쓰고, `xhigh`·`max`와 2K 이상 해상도는 이보다 비싸다고 본다.

| Quality (gpt-image-2 참고) | 1024×1024 | 1024×1536 | 1536×1024 | 2048×2048 |
|---------|-----------|-----------|-----------|-----------|
| high    | ~$0.21    | ~$0.17    | ~$0.17    | ~$0.38    |

- 한 요청의 예상 합계가 **$1 초과**(예: high 5장 이상, xhigh·max 여러 장, 2K 이상 여러 장)면 실행 전 고지하고 확인받는다. 그 이하는 진행 후 보고.
- 같은 세션에서 앞선 `[usage]` 실측치가 있으면 그 값으로 다음 요청의 예상 합계를 계산한다.
- "여러 안"은 기본 3장으로 제한한다. 더 많은 장수는 사용자가 명시했을 때만.
- 편집은 입력 이미지 토큰이 추가된다(`input_fidelity high`는 gpt-image-2에서 약 2배).

## 10. 프롬프트 작성 요령

gpt-image-2.5는 문장을 그대로 반영한다 — 구성·피사체·스타일·조명·분위기를 구체적으로. 편집 프롬프트에서는 "무엇을 유지할지"를 먼저 쓴다(2.5는 지시한 부분만 바꾸는 정밀도가 높아졌다).

- 나쁜 예: "예쁜 커피숍 로고" → 좋은 예: "미니멀한 원형 커피숍 로고, 중앙에 라떼아트 하트, 하단에 산세리프 굵은 글자로 'Morning Brew', 따뜻한 브라운-크림 팔레트, 단색 배경, 벡터 스타일"
- 렌더링할 텍스트는 **따옴표로 정확한 문구를 감싼다**.
- 편집 시 "무엇을 유지할지"를 명시한다 (예: "인물의 얼굴과 포즈는 그대로 두고 배경만 교체").
- 용도별 프롬프트 패턴(사진·인포그래픽·로고·목업·스토리보드)은 references/api_reference.md 참조.

## 11. 한계·주의

- 복잡한 프롬프트는 최대 2분까지 지연될 수 있다. sunburst와 `xhigh`·`max`는 더 오래 걸린다 — Bash 호출에 `timeout: 600000`을 지정한다.
- 텍스트 렌더링은 완벽하지 않다 — 중요한 문구는 6절 검증에서 철자를 확인하고, 필요 시 후처리 합성을 안내한다.
- 정확한 요소 배치·반복 생성 일관성은 제한적 — 레퍼런스 이미지 활용·체이닝으로 보완.
- 실재 인물·저작권 캐릭터·로고는 거부될 수 있다 — 대체 표현으로 우회 (12절).

## 12. 트러블슈팅

| 증상 | 원인 | 대응 |
|------|------|------|
| `uv: command not found` | uv 미설치 | 2절의 설치 명령 안내 후 재실행 |
| ImportError / pip 안내 문구 | 맨 python으로 직접 실행 | 표준 `uv run` 형태로 재실행. pip 설치 금지 |
| exit 2 "OPENAI_API_KEY 가 없습니다" | 키 미설정 | 사용자에게 안내: 프로젝트 루트 `.env`에 `OPENAI_API_KEY=sk-...` 한 줄을 넣거나(재시작 불필요) `export OPENAI_API_KEY` 후 Claude Code 재시작. 키 값은 노출 금지 |
| exit 2 "invalid choice: 'low'" | 품질 하한 위반 | `--quality`를 high·xhigh·max 중에서 다시 고른다(4절) |
| `[i] gpt-image-2 는 quality 상한이 high` | 구세대 모델에 xhigh·max 지정 | 스크립트가 high로 낮춰 진행한다. 최고 품질이 필요하면 `--model`을 빼서 sunburst로 실행 |
| 400 unknown model / TypeError(unexpected keyword) | 구버전 openai SDK | 스크립트의 `openai>=3.10` 선언이 지워지지 않았는지 확인. `uv run` 표준 형태로만 실행 |
| 400 `invalid_input_fidelity_model` | 2.5 모델에 `input_fidelity` 전달 | 2.5 는 미지원(스크립트 v0.3은 자동 무시). 구세대 gpt-image-2 에서만 유효 |
| 매 실행 권한 프롬프트 | allowed-tools 미매칭 | 명령을 2절 표준 문자열과 문자 단위로 일치시킨다. 지속되면 `.claude/settings.json`의 permissions.allow에 동일 규칙 등록 |
| HTTP 403 | Organization 미검증 | OpenAI 개발자 콘솔에서 Organization Verification 안내 |
| HTTP 400 크기 오류 | 16의 배수·3:1 제약 위반 | 가장 가까운 유효 크기로 보정해 재실행 |
| `content_policy_violation` | 정책 위반 | 대체 표현으로 1회 재시도, 불가 시 사유 보고 |
| HTTP 429 | 레이트리밋 | 지수 백오프로 재시도 (api_reference '오류 처리') |
| 첫 실행이 느림 | uv 환경 최초 구성 | 정상 — 이후 캐시로 즉시 실행 |
| exit 2 "덮어쓰기 거부" | 출력 경로에 기존 파일 | 파일명 버전을 올려 재실행. `--force`는 사용자가 덮어쓰기를 명시했을 때만 |

## 13. 확장 레퍼런스 · 사용자 준비

- `references/api_reference.md` — 전체 파라미터·응답 스키마·오류 코드·Python/Node/cURL 예제·프롬프트 패턴·마스크 제작 상세.
- `scripts/generate_image.py` — 생성·편집·마스킹·멀티 레퍼런스 CLI (기본 gpt-image-2.5-sunburst·quality high, `--model` 선택).
- `scripts/make_mask.py` — 기하 마스크 생성 CLI (v0.2 신규).
- 사용자 1회 준비: 프로젝트 루트에 `.env` 파일을 만들고 `OPENAI_API_KEY=sk-...` 한 줄을 넣는다(권장, 재시작 불필요) 또는 터미널에서 `export OPENAI_API_KEY="sk-..."` 후 `claude` 시작. 둘 다 있으면 환경변수가 우선한다. 프로젝트를 git으로 관리하면 `.env`를 `.gitignore`에 넣는다. 최초 사용 시 OpenAI 콘솔의 Organization Verification이 필요할 수 있다.
