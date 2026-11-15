# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib>=3.8"]
# ///
"""본문 라운드를 시험 조립해 실제 PDF 쪽수와 대목차별 시작 쪽을 잰다.

아직 만들지 않은 그림({{FIG:ID}}인데 자산 목록에 없는 것)은 유형별 비율의 임시 이미지로 채운다.
줄 수로 추정한 쪽수는 표 셀 줄바꿈·그림 배치 때문에 ±20% 이상 틀리므로, 동결 전에 이 스크립트로 실측한다.

사용(프로젝트 루트에서):
  uv run .claude/skills/bizplan-orchestrator/scripts/trial_layout.py \
      --draft "{WS}/02_writer_draft_r1.md" --manifests "{WS}/*_assets.json" \
      --out-dir "{WS}/04_trial_r1" [--width diagram-gantt=90% ...]
출력: <out-dir>/trial_제출용.pdf 등, 쪽수·대목차 시작 쪽 요약(표준 출력)
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

FIG = re.compile(r"^\s*\{\{FIG:([A-Za-z0-9_\-]+)\}\}\s*$", re.M)
# 유형별 임시 이미지 비율(가로, 세로)과 기본 폭 — 실제 산출물의 평균적인 모양
SHAPES = {"diagram": ((16, 8), "90%"), "chart": ((16, 9), "85%"), "illust": ((3, 2), "80%")}
CHAPTER = re.compile(r"^\s*([1-9])\.\s+\S+", re.M)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", required=True)
    ap.add_argument("--manifests", nargs="*", default=[])
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--width", nargs="*", default=[], help="그림ID=폭 (그림 계획의 폭을 시험 조립에 반영)")
    args = ap.parse_args()

    out = Path(args.out_dir)
    (out / "ph").mkdir(parents=True, exist_ok=True)
    assets: dict[str, dict] = {}
    for pat in args.manifests:
        for f in sorted(glob.glob(pat)):
            for e in json.loads(Path(f).read_text(encoding="utf-8")):
                assets[e["id"]] = e
    widths = dict(w.split("=", 1) for w in args.width)

    ids = FIG.findall(Path(args.draft).read_text(encoding="utf-8"))
    manifest = []
    for fid in ids:
        kind = fid.split("-", 1)[0]
        (w, h), default_width = SHAPES.get(kind, SHAPES["diagram"])
        if fid in assets and Path(assets[fid]["path"]).exists():
            e = dict(assets[fid])
        else:
            fig = plt.figure(figsize=(w / 2, h / 2))
            fig.patch.set_facecolor("#E9EDF3")
            fig.text(0.5, 0.5, f"[placeholder] {fid}", ha="center", va="center", fontsize=14)
            p = out / "ph" / f"{fid}.png"
            fig.savefig(p, dpi=60)
            plt.close(fig)
            e = {"id": fid, "type": kind, "path": str(p), "caption": f"(시험 조립용 임시) {fid}",
                 "source": "임시", "width": default_width}
        if fid in widths:
            e["width"] = widths[fid]
        manifest.append(e)
    mpath = out / "trial_assets.json"
    mpath.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")

    n = len(list(out.glob("trial*_build_report*.json"))) + 1
    name = f"trial{n}"
    build = Path(__file__).with_name("build_document.py")
    r = subprocess.run(["uv", "run", "--quiet", str(build), "--draft", args.draft, "--manifests", str(mpath),
                        "--out-dir", str(out), "--name", name, "--no-docx"], capture_output=True, text=True)
    if r.returncode not in (0, 1):
        print(r.stdout, r.stderr, file=sys.stderr)
        return r.returncode
    for variant in (f"{name}_제출용.pdf", f"{name}.pdf"):
        pdf = out / variant
        info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
        starts = []
        for i in range(1, pages + 1):
            t = subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), "-layout", str(pdf), "-"],
                               capture_output=True, text=True).stdout
            for m in re.finditer(r"^\s*([1-9])\.\s+[^\d\s][^\n]{1,20}\(", t, flags=re.M):
                starts.append(f"{m.group(1)}장→p{i}")
        print(f"[trial] {variant}: {pages}쪽 | 대목차 시작: {', '.join(starts) or '감지 못 함'}")
    placeholders = [e["id"] for e in manifest if e.get("source") == "임시"]
    print(f"[trial] 임시 그림 {len(placeholders)}개: {', '.join(placeholders)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
