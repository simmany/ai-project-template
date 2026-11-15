#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pillow",
# ]
# ///
# [v0.2 신규 | 2026-08-04 | REQ-003] 마스킹 편집용 기하 마스크 생성 헬퍼.
#   자연어 운용에서 사용자가 마스크 PNG를 만들어 줄 수 없으므로 이 스크립트가 담당한다.
#   객체 인식 기반 의미 영역("소파만")은 범위 외 — SKILL.md의 prompt-only 우선 원칙 참조.
#   설계 근거: output/03.GPT Image2 스킬 개선 검토/GPT_Image2_스킬_개선_설계_v0.2.md 4-2절
"""마스킹 편집용 마스크 PNG 생성 CLI.

규칙: 지정 영역 = 알파 0(재생성될 부분), 나머지 = 알파 255(원본 유지).
마스크는 항상 --base 이미지와 동일 해상도로 생성된다 (API 요구사항).

사용 예시.
    # 사각형 영역 (좌상 X0,Y0 우하 X1,Y1)
    uv run make_mask.py --base room.png --rect 100,200,500,600

    # 오른쪽 절반
    uv run make_mask.py --base room.png --region right --ratio 0.5

    # 원형 + 사각형 (합집합)
    uv run make_mask.py --base photo.png --circle 512,384,200 --rect 0,0,300,100

    # 흑백 마스크를 알파로 변환 (어두운 곳 = 재생성)
    uv run make_mask.py --base photo.png --from-gray mask_gray.png

    # 영역 반전 (지정 영역만 유지, 나머지 재생성)
    uv run make_mask.py --base room.png --region top --ratio 0.3 --invert
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _usage_error(msg: str) -> None:
    print(f"[!] {msg}", file=sys.stderr)
    sys.exit(2)


def _parse_ints(text: str, count: int, label: str) -> list[int]:
    parts = text.split(",")
    if len(parts) != count:
        _usage_error(f"{label} 형식 오류: '{text}' (정수 {count}개를 쉼표로 구분)")
    try:
        return [int(p.strip()) for p in parts]
    except ValueError:
        _usage_error(f"{label} 형식 오류: '{text}' (정수만 허용)")
    return []  # 도달하지 않음


def build_mask(base_size, rects, circles, region, ratio, from_gray, invert):
    """알파 0 = 재생성, 255 = 유지인 RGBA 마스크 생성."""
    from PIL import Image, ImageDraw, ImageOps

    w, h = base_size

    if from_gray:
        gray = Image.open(from_gray).convert("L")
        if gray.size != base_size:
            # 해상도 불일치는 API 오류가 되므로 base 크기로 맞춘다
            print(f"  [i] {from_gray} 크기를 {w}x{h}로 조정", file=sys.stderr)
            gray = gray.resize(base_size)
        if invert:
            gray = ImageOps.invert(gray)
        alpha = gray  # 어두운 곳(0) = 투명 = 재생성
    else:
        alpha = Image.new("L", base_size, 255)
        draw = ImageDraw.Draw(alpha)
        for x0, y0, x1, y1 in rects:
            draw.rectangle([x0, y0, x1, y1], fill=0)
        for cx, cy, r in circles:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=0)
        if region:
            if region == "top":
                box = [0, 0, w, int(h * ratio)]
            elif region == "bottom":
                box = [0, h - int(h * ratio), w, h]
            elif region == "left":
                box = [0, 0, int(w * ratio), h]
            else:  # right
                box = [w - int(w * ratio), 0, w, h]
            draw.rectangle(box, fill=0)
        if invert:
            alpha = ImageOps.invert(alpha)

    rgba = Image.new("RGBA", base_size, (0, 0, 0, 255))
    rgba.putalpha(alpha)
    return rgba


def _transparent_ratio(rgba) -> float:
    hist = rgba.getchannel("A").histogram()
    total = sum(hist)
    return (hist[0] / total) if total else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="마스킹 편집용 마스크 PNG 생성 (알파 0 영역이 재생성됨)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--base", required=True,
                        help="원본 이미지 (마스크 크기의 기준)")
    parser.add_argument("--rect", action="append", default=[],
                        metavar="X0,Y0,X1,Y1", help="사각형 영역 (반복 가능)")
    parser.add_argument("--circle", action="append", default=[],
                        metavar="CX,CY,R", help="원형 영역 (반복 가능)")
    parser.add_argument("--region", choices=["top", "bottom", "left", "right"],
                        help="가장자리 띠 영역")
    parser.add_argument("--ratio", type=float, default=0.5,
                        help="--region 띠의 비율 0~1 (기본 0.5)")
    parser.add_argument("--from-gray", dest="from_gray",
                        help="그레이스케일 마스크를 알파로 변환 (어두운 곳=재생성)")
    parser.add_argument("--invert", action="store_true", help="영역 반전")
    parser.add_argument("--output", "-o", default="mask.png",
                        help="출력 경로 (기본 mask.png)")
    parser.add_argument("--force", action="store_true",
                        help="기존 출력 파일 덮어쓰기 허용 (기본은 거부)")

    args = parser.parse_args()

    base_path = Path(args.base)
    if not base_path.exists():
        _usage_error(f"기준 이미지 없음: {base_path}")
    if not (args.rect or args.circle or args.region or args.from_gray):
        _usage_error("영역 지정 필요: --rect / --circle / --region / --from-gray 중 하나 이상")
    if args.from_gray and (args.rect or args.circle or args.region):
        _usage_error("--from-gray는 기하 영역 옵션(--rect/--circle/--region)과 함께 쓸 수 없습니다")
    if args.from_gray and not Path(args.from_gray).exists():
        _usage_error(f"그레이스케일 마스크 없음: {args.from_gray}")
    if args.region and not (0 < args.ratio <= 1):
        _usage_error(f"--ratio 범위 오류: {args.ratio} (0 초과 1 이하)")

    rects = [_parse_ints(r, 4, "--rect") for r in args.rect]
    for x0, y0, x1, y1 in rects:
        if not (x0 < x1 and y0 < y1):
            _usage_error(f"--rect 좌표 오류: {x0},{y0},{x1},{y1} (X0<X1, Y0<Y1)")
    circles = [_parse_ints(c, 3, "--circle") for c in args.circle]
    for cx, cy, r in circles:
        if r <= 0:
            _usage_error(f"--circle 반지름 오류: {cx},{cy},{r} (R>0)")

    out = Path(args.output)
    if out.exists() and not args.force:
        print(f"[!] 덮어쓰기 거부: {out} 이미 존재. "
              "다른 --output을 쓰거나 --force를 지정하세요.", file=sys.stderr)
        return 2

    try:
        from PIL import Image

        base = Image.open(base_path)
        mask = build_mask(base.size, rects, circles, args.region, args.ratio,
                          args.from_gray, args.invert)
        out.parent.mkdir(parents=True, exist_ok=True)
        mask.save(out, format="PNG")
    except ImportError:
        print(
            "[!] pillow 패키지를 준비하지 못했습니다. "
            f'`uv run "{Path(__file__).resolve()}" ...` 형태로 실행하세요.',
            file=sys.stderr,
        )
        return 2
    except SystemExit:
        raise
    except Exception as e:
        print(f"[!] 실패: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    print(out)
    print(f"  {mask.size[0]}x{mask.size[1]} / 재생성(투명) 비율 "
          f"{_transparent_ratio(mask):.1%}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
