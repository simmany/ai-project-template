#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "openai>=3.10",
#   "python-dotenv>=1.0",
# ]
# ///
# [v0.4 | 2026-09-28] 품질 우선 정책. 변경점은 [v0.4] 주석으로 표시.
#   - 기본 모델 gpt-image-2.5-flare → gpt-image-2.5-sunburst (OpenAI 문서상 "the most capable model")
#   - quality 선택지를 high·xhigh·max 로 제한, 기본 high (low·medium·auto 는 argparse 가 거부)
#   - OPENAI_API_KEY: 환경변수 → .env(현재 디렉터리 → 프로젝트 루트). ~/.config/openai/.env 폴백 제거
#   - openai>=3.10 하한 (GPT Image 2.5 지원 SDK). uv 캐시에 남은 구버전 SDK 재사용 방지
#   - .env 파싱을 python-dotenv 로 교체 (인라인 주석·따옴표·export 처리)
#   - 기본 출력 경로 generated_images/, --output 확장자로 형식 추론, 적용 설정·사용 토큰·추정 비용 stderr 출력
# [v0.3 | 2026-09-11 | REQ-002] ChatGPT Images 2.5 대응. 변경점은 [v0.3] 주석으로 표시.
#   - 기본 모델 gpt-image-2 → gpt-image-2.5-flare, --model 로 gpt-image-2.5-sunburst(정밀 편집)·gpt-image-2(구세대) 선택
#   - quality 에 xhigh·max 추가, --background(auto/opaque/transparent), --input-fidelity(auto/high) 옵션 신설
#   - OPENAI_API_KEY 가 환경에 없으면 ./.env → ~/.config/openai/.env 순으로 읽는 폴백 (값은 절대 출력하지 않음)
#   근거: developers.openai.com/api/docs/models/gpt-image-2.5-flare · …/gpt-image-2.5-sunburst · …/guides/image-generation (2026-09 확인)
# [v0.2 | 2026-08-04 | REQ-003] 외부 작성 원본을 개선. 변경점은 [v0.2] 주석으로 표시.
#   - PEP 723 인라인 의존성 선언 → uv 격리 실행 (pip 전역 설치 폐지)
#   - ImportError 안내를 uv run 형태로 교체, docstring 예시를 uv run으로 통일
#   - --force 덮어쓰기 가드 신설 (기존 출력 파일 보호, API 호출 전 검사)
#   설계 근거: output/03.GPT Image2 스킬 개선 검토/GPT_Image2_스킬_개선_설계_v0.2.md
"""OpenAI GPT Image 2.5 이미지 생성·편집 CLI.

기본 모델은 ``gpt-image-2.5-sunburst`` (최고 성능). 사용자가 속도를 우선하면
``--model gpt-image-2.5-flare``, 구세대가 필요하면 ``--model gpt-image-2``.
quality 는 high(기본)·xhigh·max 만 받는다.
API 키는 환경변수 OPENAI_API_KEY, 없으면 .env(현재 디렉터리 → 프로젝트 루트)에서 읽는다.

사용 예시.
    # 텍스트 → 이미지 (sunburst, quality high)
    uv run generate_image.py "귀여운 고양이가 책을 읽는 모습"

    # 크기·품질 지정 (quality: high/xhigh/max)
    uv run generate_image.py "로고 디자인" --size 1024x1024 --quality xhigh --output logo.png

    # 투명 배경(png·webp)
    uv run generate_image.py "배경을 지워줘" --input logo.png --background transparent

    # 편집 (단일 이미지, 프롬프트만)
    uv run generate_image.py "배경을 바다로 바꿔줘" --input photo.png --output edited.png

    # 마스킹 편집 (투명 영역만 재생성)
    uv run generate_image.py "빈 공간에 소파" --input room.png --mask mask.png

    # 멀티 레퍼런스 합성
    uv run generate_image.py "선물 바구니" --input lotion.png soap.png candle.png

    # 여러 장 한번에
    uv run generate_image.py "미니멀 아이콘 세트" --n 4

    # 스트리밍 (중간 이미지도 저장)
    uv run generate_image.py "흐르는 강" --stream --partial 2
"""

from __future__ import annotations

import argparse
import base64
import os
import sys
from datetime import datetime
from pathlib import Path


# [v0.4] 기본 sunburst. flare 는 속도 우선 요청, gpt-image-2 는 구세대 호환용.
MODELS = ("gpt-image-2.5-sunburst", "gpt-image-2.5-flare", "gpt-image-2")
MODEL_DEFAULT = "gpt-image-2.5-sunburst"
# [v0.4] 품질 하한 high. xhigh·max 는 2.5 전용이고 gpt-image-2 는 high 가 상한이다.
QUALITIES = ("high", "xhigh", "max")
QUALITY_DEFAULT = "high"
BACKGROUNDS = ("auto", "opaque", "transparent")
FORMATS = ("png", "jpeg", "webp")
SUFFIX_FORMATS = {".png": "png", ".jpg": "jpeg", ".jpeg": "jpeg", ".webp": "webp"}
DEFAULT_OUTPUT_DIR = Path("generated_images")  # [v0.4] --output 미지정 시 저장 위치
# [v0.4] USD / 1M 토큰. gpt-image-2.5(flare·sunburst)와 gpt-image-2 공통 (2026-09 공식 문서)
PRICE_PER_M = {"text_in": 5.0, "image_in": 8.0, "image_out": 30.0}


def _usage_error(msg: str) -> int:
    print(f"[!] {msg}", file=sys.stderr)
    return 2


def _missing_dependency(package: str) -> int:
    # [v0.2] pip 전역 설치 안내 폐지 → uv 격리 실행 안내 (자기 경로 삽입)
    return _usage_error(
        f"{package} 패키지를 준비하지 못했습니다. "
        f'`uv run "{Path(__file__).resolve()}" ...` 형태로 실행하세요.'
    )


def _project_root() -> Path:
    # scripts → gpt-image2 → skills → .claude → 프로젝트 루트
    here = Path(__file__).resolve()
    return here.parents[4] if len(here.parents) > 4 else Path.cwd()


def _load_api_key() -> bool:
    """[v0.4] 환경변수 우선, 없으면 .env(현재 디렉터리 → 프로젝트 루트). 값은 절대 출력하지 않는다."""
    if os.environ.get("OPENAI_API_KEY"):
        return True
    from dotenv import dotenv_values

    candidates = dict.fromkeys([Path.cwd().resolve() / ".env", _project_root() / ".env"])
    for env_path in candidates:
        if not env_path.is_file():
            continue
        value = dotenv_values(env_path).get("OPENAI_API_KEY")
        if value:
            os.environ["OPENAI_API_KEY"] = value
            return True
    return False


def _save_b64(b64: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64decode(b64))


def _resolve_output_paths(output: str | None, n: int, ext: str) -> list[Path]:
    if output:
        base = Path(output)
        if not base.suffix:
            base = base.with_suffix(f".{ext}")
        if n == 1:
            return [base]
        stem, suffix = base.stem, base.suffix or f".{ext}"
        return [base.with_name(f"{stem}_{i+1}{suffix}") for i in range(n)]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    if n == 1:
        return [DEFAULT_OUTPUT_DIR / f"gpt_image_{ts}.{ext}"]
    return [DEFAULT_OUTPUT_DIR / f"gpt_image_{ts}_{i+1}.{ext}" for i in range(n)]


def _check_overwrite(paths: list[Path], force: bool) -> None:
    # [v0.2] 덮어쓰기 가드. API 호출 전에 검사해 비용 낭비를 막는다.
    existing = [str(p) for p in paths if p.exists()]
    if existing and not force:
        print(
            f"[!] 덮어쓰기 거부: {', '.join(existing)} 이미 존재. "
            "다른 파일명을 쓰거나 --force를 지정하세요.",
            file=sys.stderr,
        )
        sys.exit(2)


def _report_usage(usage) -> None:
    """[v0.4] 응답의 토큰 사용량으로 추정 비용을 stderr 에 출력한다 (2.5 는 공식 장당 가격표가 없음)."""
    if not usage:
        return
    details = getattr(usage, "input_tokens_details", None)
    text_in = getattr(details, "text_tokens", None)
    image_in = getattr(details, "image_tokens", None) or 0
    if text_in is None:
        text_in = getattr(usage, "input_tokens", 0) or 0
    image_out = getattr(usage, "output_tokens", 0) or 0
    cost = (
        text_in * PRICE_PER_M["text_in"]
        + image_in * PRICE_PER_M["image_in"]
        + image_out * PRICE_PER_M["image_out"]
    ) / 1_000_000
    print(
        f"  [usage] 입력 텍스트 {text_in} · 입력 이미지 {image_in} · 출력 {image_out} 토큰 "
        f"≈ ${cost:.3f}",
        file=sys.stderr,
    )


def generate(
    prompt: str,
    size: str = "auto",
    quality: str = QUALITY_DEFAULT,
    n: int = 1,
    output_format: str = "png",
    output_compression: int | None = None,
    moderation: str | None = None,
    output: str | None = None,
    force: bool = False,
    model: str = MODEL_DEFAULT,
    background: str | None = None,
) -> list[Path]:
    """텍스트 → 이미지 생성."""
    from openai import OpenAI

    paths = _resolve_output_paths(output, n, output_format)
    _check_overwrite(paths, force)  # [v0.2]

    kwargs = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "size": size,
        "quality": quality,
        "output_format": output_format,
    }
    if output_compression is not None and output_format in {"jpeg", "webp"}:
        kwargs["output_compression"] = output_compression
    if moderation:
        kwargs["moderation"] = moderation
    if background and background != "auto":
        kwargs["background"] = background

    result = OpenAI().images.generate(**kwargs)

    for i, data in enumerate(result.data):
        _save_b64(data.b64_json, paths[i])
    _report_usage(getattr(result, "usage", None))
    return paths[: len(result.data)]


def edit(
    prompt: str,
    images: list[str],
    mask: str | None = None,
    size: str = "auto",
    quality: str = QUALITY_DEFAULT,
    n: int = 1,
    output_format: str = "png",
    output_compression: int | None = None,
    output: str | None = None,
    force: bool = False,
    model: str = MODEL_DEFAULT,
    input_fidelity: str | None = None,
    background: str | None = None,
) -> list[Path]:
    """이미지 편집 (단일/멀티 레퍼런스, 선택적 마스크)."""
    from openai import OpenAI

    paths = _resolve_output_paths(output, n, output_format)
    _check_overwrite(paths, force)  # [v0.2] 입력 열기·API 호출 전 검사

    client = OpenAI()

    opened = [open(p, "rb") for p in images]
    mask_fh = open(mask, "rb") if mask else None
    try:
        kwargs = {
            "model": model,
            "image": opened[0] if len(opened) == 1 else opened,
            "prompt": prompt,
            "n": n,
            "size": size,
            "quality": quality,
            "output_format": output_format,
        }
        if output_compression is not None and output_format in {"jpeg", "webp"}:
            kwargs["output_compression"] = output_compression
        if mask_fh:
            kwargs["mask"] = mask_fh
        if input_fidelity:
            if model.startswith("gpt-image-2.5"):
                # [v0.3] 2.5 계열은 input_fidelity 파라미터를 거부한다(400 invalid_input_fidelity_model). 기본이 고충실도이므로 무시.
                print("[i] gpt-image-2.5 는 input_fidelity 를 지원하지 않아 무시합니다.", file=sys.stderr)
            else:
                kwargs["input_fidelity"] = input_fidelity
        if background and background != "auto":
            kwargs["background"] = background
        result = client.images.edit(**kwargs)
    finally:
        for fh in opened:
            fh.close()
        if mask_fh:
            mask_fh.close()

    for i, data in enumerate(result.data):
        _save_b64(data.b64_json, paths[i])
    _report_usage(getattr(result, "usage", None))
    return paths[: len(result.data)]


def stream_generate(
    prompt: str,
    size: str = "auto",
    quality: str = QUALITY_DEFAULT,
    partial_images: int = 2,
    output_format: str = "png",
    output: str | None = None,
    force: bool = False,
    model: str = MODEL_DEFAULT,
) -> list[Path]:
    """스트리밍으로 중간·최종 이미지 저장."""
    from openai import OpenAI

    out_path = _resolve_output_paths(output, 1, output_format)[0]
    _check_overwrite([out_path], force)  # [v0.2] 호출 전 최종 경로 가드
    saved: list[Path] = []

    stream = OpenAI().images.generate(
        model=model,
        prompt=prompt,
        size=size,
        quality=quality,
        output_format=output_format,
        stream=True,
        partial_images=partial_images,
    )
    for event in stream:
        etype = getattr(event, "type", "")
        if etype == "image_generation.partial_image":
            idx = getattr(event, "partial_image_index", len(saved))
            p = out_path.with_name(f"{out_path.stem}_partial{idx}{out_path.suffix}")
            _save_b64(event.b64_json, p)
            saved.append(p)
            print(f"  partial {idx} → {p}", file=sys.stderr)
        elif etype in {"image_generation.completed", "image_generation.final_image"}:
            _save_b64(event.b64_json, out_path)
            saved.append(out_path)
            _report_usage(getattr(event, "usage", None))
    return saved


def main() -> int:
    parser = argparse.ArgumentParser(
        description=f"OpenAI GPT Image 2.5 CLI (default model {MODEL_DEFAULT}, quality {QUALITY_DEFAULT})",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("prompt", help="이미지 생성·편집 프롬프트")
    parser.add_argument("--size", default="auto",
                        help='크기 예: 1024x1024, 1536x1024, 1024x1536, auto')
    parser.add_argument("--quality", default=QUALITY_DEFAULT, choices=list(QUALITIES),
                        help="[v0.4] high(기본)·xhigh·max 만 허용")
    parser.add_argument("--model", default=MODEL_DEFAULT, choices=list(MODELS),
                        help="[v0.4] 기본 sunburst(최고 성능) / flare(속도 우선) / gpt-image-2(구세대)")
    parser.add_argument("--background", default=None, choices=list(BACKGROUNDS),
                        help="transparent 는 png/webp 전용")
    parser.add_argument("--input-fidelity", dest="input_fidelity", default=None,
                        choices=["high", "low"], help="gpt-image-2 편집 전용 (2.5 는 무시)")
    parser.add_argument("--n", type=int, default=1, help="생성 장수")
    parser.add_argument("--output", "-o", help="출력 파일 경로 (미지정 시 generated_images/)")
    parser.add_argument("--format", dest="output_format", default=None, choices=list(FORMATS),
                        help="[v0.4] 미지정 시 --output 확장자로 추론, 없으면 png")
    parser.add_argument("--compression", type=int, default=None,
                        help="jpeg/webp 압축 0-100")
    parser.add_argument("--moderation", choices=["auto", "low"], help="생성 전용")
    parser.add_argument("--input", "-i", nargs="+",
                        help="편집할 입력 이미지(여러 개 가능)")
    parser.add_argument("--mask", help="마스크 PNG (투명 영역만 재생성)")
    parser.add_argument("--stream", action="store_true",
                        help="스트리밍 모드 (중간 이미지 저장, 생성 전용)")
    parser.add_argument("--partial", type=int, default=2,
                        help="스트리밍 시 중간 이미지 개수 (0-3)")
    parser.add_argument("--force", action="store_true",
                        help="기존 출력 파일 덮어쓰기 허용 ([v0.2] 기본은 거부)")

    args = parser.parse_args()

    # [v0.4] API 호출 전 사용 오류를 모두 걸러 exit 2 로 끝낸다.
    inferred = SUFFIX_FORMATS.get(Path(args.output).suffix.lower()) if args.output else None
    if args.output_format is None:
        args.output_format = inferred or "png"
    elif inferred and inferred != args.output_format:
        return _usage_error(f"--output 확장자와 --format {args.output_format} 이 다릅니다")
    if args.background == "transparent" and args.output_format == "jpeg":
        return _usage_error("transparent 배경은 png/webp 에서만 가능합니다")
    if args.stream and args.input:
        return _usage_error("--stream은 생성 전용입니다. --input과 함께 쓸 수 없습니다.")
    if args.mask and not args.input:
        return _usage_error("--mask는 --input과 함께 써야 합니다")
    for p in (args.input or []) + ([args.mask] if args.mask else []):
        if not Path(p).is_file():
            return _usage_error(f"입력 파일 없음: {p}")
    if args.model == "gpt-image-2" and args.quality != "high":
        print(f"[i] gpt-image-2 는 quality 상한이 high 라 {args.quality} → high 로 조정합니다.",
              file=sys.stderr)
        args.quality = "high"

    try:
        if not _load_api_key():  # [v0.4] env → ./.env → 프로젝트 루트 .env
            return _usage_error(
                "OPENAI_API_KEY 가 없습니다. 환경변수로 설정하거나 프로젝트 루트 .env 에 "
                "OPENAI_API_KEY=sk-... 한 줄을 넣으세요."
            )
    except ImportError:
        return _missing_dependency("python-dotenv")

    print(f"  [settings] model={args.model} quality={args.quality} size={args.size} "
          f"format={args.output_format}", file=sys.stderr)

    try:
        if args.stream:
            paths = stream_generate(
                args.prompt,
                size=args.size,
                quality=args.quality,
                partial_images=args.partial,
                output_format=args.output_format,
                output=args.output,
                force=args.force,
                model=args.model,
            )
        elif args.input:
            paths = edit(
                args.prompt,
                images=args.input,
                mask=args.mask,
                size=args.size,
                quality=args.quality,
                n=args.n,
                output_format=args.output_format,
                output_compression=args.compression,
                output=args.output,
                force=args.force,
                model=args.model,
                input_fidelity=args.input_fidelity,
                background=args.background,
            )
        else:
            paths = generate(
                args.prompt,
                size=args.size,
                quality=args.quality,
                n=args.n,
                output_format=args.output_format,
                output_compression=args.compression,
                moderation=args.moderation,
                output=args.output,
                force=args.force,
                model=args.model,
                background=args.background,
            )
    except ImportError:
        return _missing_dependency("openai")
    except Exception as e:
        print(f"[!] 실패: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    for p in paths:
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
