"""사업계획서 차트 공통 스타일 — 한글 글꼴, 프로젝트 팔레트, 출처 표기, 덮어쓰기 방지.

사용:
    import sys
    sys.path.insert(0, ".claude/skills/data-file-analysis/scripts")
    from kr_chart_style import apply_style, PALETTE, save_fig
    apply_style()
    ...
    save_fig(fig, "output/.../chart_x_v1.png", title="결론형 제목", source="출처: ...")

팔레트 값은 .claude/skills/bizplan-orchestrator/references/visual-system.md 와 같게 유지한다.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

PALETTE = {
    "PRIMARY": "#1B2A4A",
    "SECONDARY": "#2E86AB",
    "ACCENT": "#F26B38",
    "ECO": "#3BAA6E",
    "NEUTRAL": "#8C96A8",
    "NEUTRAL_LIGHT": "#C3C9D4",
    "LIGHT": "#E9EDF3",
    "WARN": "#C8553D",
}

FONT_CANDIDATES = [
    "Pretendard",
    "Apple SD Gothic Neo",
    "Noto Sans KR",
    "NanumGothic",
    "NanumBarunGothic",
    "Malgun Gothic",
]


def _pick_font() -> str | None:
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in FONT_CANDIDATES:
        if name in available:
            return name
    return None


def apply_style() -> str | None:
    """한글 글꼴과 기본 스타일을 적용하고 선택한 글꼴 이름을 반환한다."""
    font = _pick_font()
    if font:
        plt.rcParams["font.family"] = font
    plt.rcParams.update(
        {
            "axes.unicode_minus": False,
            "figure.dpi": 100,
            "savefig.dpi": 200,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": PALETTE["NEUTRAL"],
            "axes.labelcolor": PALETTE["PRIMARY"],
            "axes.titleweight": "bold",
            "axes.titlesize": 14,
            "axes.labelsize": 10.5,
            "xtick.color": PALETTE["PRIMARY"],
            "ytick.color": PALETTE["PRIMARY"],
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.frameon": False,
            "legend.fontsize": 9.5,
            "grid.color": PALETTE["LIGHT"],
            "grid.linewidth": 0.8,
        }
    )
    if font is None:
        print("[warn] 한글 글꼴을 찾지 못했습니다. 글자가 깨질 수 있습니다.")
    return font


def save_fig(fig, path: str, title: str | None = None, source: str | None = None, force: bool = False) -> Path:
    """결론형 제목과 출처를 달아 PNG로 저장한다. 같은 파일이 있으면 덮어쓰지 않는다."""
    out = Path(path)
    if out.exists() and not force:
        raise FileExistsError(f"이미 있는 파일입니다(덮어쓰기 금지): {out} — 버전을 올려 저장하세요.")
    out.parent.mkdir(parents=True, exist_ok=True)
    if title:
        fig.suptitle(title, x=0.02, ha="left", fontsize=15, fontweight="bold", color=PALETTE["PRIMARY"])
    if source:
        fig.text(0.02, 0.01, source, ha="left", va="bottom", fontsize=8.5, color=PALETTE["NEUTRAL"])
    fig.tight_layout(rect=(0, 0.04 if source else 0, 1, 0.96 if title else 1))
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[saved] {out}")
    return out
