# /// script
# requires-python = ">=3.10"
# dependencies = ["pypandoc-binary>=1.13"]
# ///
"""사업계획서 본문(마크다운)을 그림과 함께 조립해 MD·HTML·PDF·DOCX로 만든다.

- 본문의 `{{FIG:그림ID}}` 단독 줄을 자산 목록(*_assets.json)의 이미지로 바꾸고 "그림 N." 번호를 붙인다.
- 검토용(메모 포함)과 제출용(`>` 인용 블록 메모와 '제출본 제외' 절 제거) 두 가지를 만든다.
- 같은 이름의 산출물이 있으면 덮어쓰지 않는다(--force로만 허용).

사용(프로젝트 루트에서):
  uv run .claude/skills/bizplan-orchestrator/scripts/build_document.py \
      --draft "output/01_사업계획서_초안/_workspace/v1/05_frozen_draft.md" \
      --manifests "output/01_사업계획서_초안/_workspace/v1/*_assets.json" \
      --out-dir "output/01_사업계획서_초안/drafts" --name "사업계획서_초안_v1"
종료 코드: 0 성공 / 1 변환 실패 / 2 사용 오류(입력 없음, 덮어쓰기 거부)
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import pypandoc

FIG_LINE = re.compile(r"^\s*\{\{FIG:([A-Za-z0-9_\-]+)\}\}\s*$")
CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]

CSS = """
@page { size: A4; margin: 14mm 15mm 15mm 15mm; }
html { font-size: 10pt; }
body { font-family: Pretendard, 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
       color: #1B2A4A; line-height: 1.5; max-width: 182mm; margin: 0 auto; padding: 6mm 0; background: #FFFFFF;
       word-break: keep-all; }
h1 { font-size: 19pt; line-height: 1.35; border-bottom: 3px solid #1B2A4A; padding-bottom: 8px; margin: 0 0 14px; }
h2 { font-size: 13.5pt; color: #FFFFFF; background: #1B2A4A; padding: 6px 12px; margin: 22px 0 10px; break-after: avoid; }
h3 { font-size: 11.8pt; border-left: 5px solid #F26B38; padding-left: 9px; margin: 16px 0 6px; break-after: avoid; }
h4 { font-size: 10.8pt; color: #2E86AB; margin: 12px 0 4px; break-after: avoid; }
p { margin: 4px 0; }
ul, ol { margin: 3px 0 6px; padding-left: 18px; }
li { margin: 1px 0; }
strong { color: #1B2A4A; }
table { border-collapse: collapse; width: 100%; margin: 6px 0 10px; font-size: 8.5pt; line-height: 1.38; }
tr { break-inside: avoid; }
th { background: #E9EDF3; color: #1B2A4A; font-weight: 700; }
th, td { border: 1px solid #C3C9D4; padding: 2px 5px; vertical-align: top; }
tr:nth-child(even) td { background: #FAFBFD; }
blockquote { margin: 6px 0 10px; padding: 5px 10px; background: #FFF4EE; border-left: 3px solid #F26B38;
             color: #5A4036; font-size: 8.8pt; break-inside: avoid; }
blockquote p { margin: 2px 0; }
figure { margin: 8px 0 10px; text-align: center; break-inside: avoid; }
figure img { max-width: 100%; height: auto; }
figcaption { font-size: 8.8pt; color: #5B6B82; margin-top: 4px; }
code { font-size: 8.8pt; }
.fig-missing { color: #C8553D; font-weight: 700; }
"""


def die(msg: str, code: int = 2) -> None:
    print(f"[error] {msg}", file=sys.stderr)
    sys.exit(code)


def load_manifests(patterns: list[str]) -> dict[str, dict]:
    assets: dict[str, dict] = {}
    files: list[str] = []
    replaced = 0
    for pat in patterns:
        files.extend(sorted(glob.glob(pat)))
    if not files:
        print("[warn] 자산 목록(*_assets.json)을 찾지 못했습니다. 모든 그림이 자리 표시로 남습니다.")
    for f in files:
        try:
            entries = json.loads(Path(f).read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"[warn] JSON 오류로 건너뜀: {f} ({e})")
            continue
        for e in entries if isinstance(entries, list) else []:
            fid = e.get("id")
            if not fid or not e.get("path"):
                print(f"[warn] id·path가 없는 항목을 건너뜀: {f}")
                continue
            if fid in assets:
                replaced += 1
            assets[fid] = {**e, "_manifest": f}
    print(f"[info] 자산 목록 {len(files)}개, 그림 {len(assets)}개 로드 (같은 ID를 나중 파일 값으로 대체 {replaced}건)")
    return assets


def resolve_figures(text: str, assets: dict[str, dict], out_dir: Path) -> tuple[str, list[dict], list[str]]:
    lines, used, missing, n = [], [], [], 0
    for line in text.splitlines():
        m = FIG_LINE.match(line)
        if not m:
            lines.append(line)
            continue
        fid = m.group(1)
        a = assets.get(fid)
        if not a or not Path(a["path"]).exists():
            missing.append(fid)
            lines.append(f'<p class="fig-missing">[그림 삽입: {fid} — 자산 없음]</p>')
            continue
        n += 1
        rel = os.path.relpath(Path(a["path"]).resolve(), out_dir.resolve())
        caption = a.get("caption", "").strip()
        source = a.get("source", "").strip()
        label = f"그림 {n}. {caption}" + (f" (출처: {source})" if source else "")
        label = label.replace("[", "(").replace("]", ")")
        width = a.get("width", "90%")
        lines += ["", f"![{label}]({rel}){{width={width}}}", ""]
        used.append({"no": n, "id": fid, "path": a["path"]})
    return "\n".join(lines) + "\n", used, missing


TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
INTERNAL_HEADING = re.compile(r"^(#{1,6})\s+.*(제출본 제외|작성 메모|내부 메모)")


def ensure_table_blank_lines(text: str) -> str:
    """표 제목 줄 바로 다음에 표가 붙어 있으면 빈 줄을 넣는다. 빈 줄이 없으면 pandoc이 표를 문단으로 읽는다."""
    lines = text.splitlines()
    out: list[str] = []
    for i, line in enumerate(lines):
        is_table_start = (line.lstrip().startswith("|") and i + 1 < len(lines) and TABLE_SEP.match(lines[i + 1]))
        if is_table_start and out and out[-1].strip() and not out[-1].lstrip().startswith("|"):
            out.append("")
        out.append(line)
    return "\n".join(out) + "\n"


def strip_internal_sections(text: str) -> str:
    """제출용에서 '제출본 제외'·'작성 메모' 제목이 붙은 절을 다음 같은 수준 이상의 제목 전까지 지운다."""
    out: list[str] = []
    skip_level = 0
    for line in text.splitlines():
        h = re.match(r"^(#{1,6})\s", line)
        if skip_level and h and len(h.group(1)) <= skip_level:
            skip_level = 0
        m = INTERNAL_HEADING.match(line)
        if m:
            skip_level = len(m.group(1))
            while out and out[-1].strip() in ("", "---", "***"):
                out.pop()
            continue
        if not skip_level:
            out.append(line)
    return "\n".join(out) + "\n"


TAG_LINK = re.compile(r"(\[(?:확인 필요|가정|창업자 입력 필요)[^\]]*\])\(")


def protect_tag_parens(text: str) -> str:
    """`[창업자 입력 필요](설명)`처럼 태그 바로 뒤 괄호가 마크다운 링크로 읽혀 글자가 사라지는 것을 막는다."""
    return TAG_LINK.sub(r"\1 (", text)


def strip_memos(text: str) -> str:
    """제출용에서 `>` 인용 블록을 모두 지운다. 사업계획서 본문에서 인용 블록은 작성용 메모 전용이다.
    메모를 지우고 나면 제목 바로 뒤나 연속으로 남는 구분선(---)도 함께 지운다(이중선 방지)."""
    out: list[str] = []
    for line in text.splitlines():
        if line.lstrip().startswith(">"):
            continue
        if line.strip() in ("---", "***"):
            prev = next((p for p in reversed(out) if p.strip()), "")
            if not prev or prev.startswith("#") or prev.strip() in ("---", "***"):
                continue
        out.append(line)
    return "\n".join(out) + "\n"


def korean_reference_docx(dest: Path) -> Path:
    """pandoc 기본 reference.docx의 글꼴을 맑은 고딕으로 바꾼 사본을 만든다(평가위원 PC 기본 글꼴)."""
    pandoc = pypandoc.get_pandoc_path()
    raw = subprocess.run([pandoc, "--print-default-data-file", "reference.docx"], capture_output=True, check=True).stdout
    src = dest.with_suffix(".orig.docx")
    src.write_bytes(raw)
    font = "Malgun Gothic"
    rfonts = f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:eastAsia="{font}" w:cs="{font}"/>'
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/styles.xml":
                xml = data.decode("utf-8")
                xml = re.sub(r"<w:rFonts\b[^>]*/>", rfonts, xml)
                data = xml.encode("utf-8")
            zout.writestr(item, data)
    src.unlink()
    return dest


def find_chrome() -> str | None:
    for c in CHROME_CANDIDATES:
        if c and os.access(c, os.X_OK):
            return c
    return None


def html_to_pdf(html: Path, pdf: Path) -> bool:
    chrome = find_chrome()
    if not chrome:
        print("[warn] Chrome/Chromium이 없어 PDF를 건너뜁니다.")
        return False
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf-no-header",
           f"--print-to-pdf={pdf}", html.resolve().as_uri()]
    subprocess.run(cmd, capture_output=True, timeout=180)
    return pdf.exists() and pdf.stat().st_size > 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--draft", required=True, help="동결된 본문 마크다운")
    ap.add_argument("--manifests", nargs="*", default=[], help="자산 목록 JSON 경로 또는 glob (여러 개)")
    ap.add_argument("--out-dir", required=True, help="산출물 폴더 (예: output/01_사업계획서_초안/drafts)")
    ap.add_argument("--name", required=True, help="파일 이름 (확장자 제외, 예: 사업계획서_초안_v1)")
    ap.add_argument("--no-pdf", action="store_true")
    ap.add_argument("--no-docx", action="store_true")
    ap.add_argument("--force", action="store_true", help="기존 산출물 덮어쓰기 허용(사용자가 명시했을 때만)")
    args = ap.parse_args()

    draft = Path(args.draft)
    if not draft.exists():
        die(f"본문 파일이 없습니다: {draft}")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    variants = {"검토용": args.name, "제출용": f"{args.name}_제출용"}
    targets = []
    for base in variants.values():
        targets += [out_dir / f"{base}.md", out_dir / f"{base}.html"]
        if not args.no_pdf:
            targets.append(out_dir / f"{base}.pdf")
        if not args.no_docx:
            targets.append(out_dir / f"{base}.docx")
    existing = [str(t) for t in targets if t.exists()]
    if existing and not args.force:
        die("이미 있는 산출물입니다(덮어쓰기 금지). 버전을 올리세요:\n  " + "\n  ".join(existing))

    assets = load_manifests(args.manifests)
    raw = protect_tag_parens(ensure_table_blank_lines(draft.read_text(encoding="utf-8")))
    body, used, missing = resolve_figures(raw, assets, out_dir)
    m = re.search(r"^#\s+(.+)$", body, flags=re.M)
    title = m.group(1).strip() if m else args.name

    tmp = Path(tempfile.mkdtemp(prefix="bizplan_build_"))
    css = tmp / "style.css"
    css.write_text(CSS, encoding="utf-8")
    ref_docx = None if args.no_docx else korean_reference_docx(tmp / "reference.docx")

    outputs, failures = [], []
    for kind, base in variants.items():
        text = body if kind == "검토용" else strip_internal_sections(strip_memos(body))
        md = out_dir / f"{base}.md"
        md.write_text(text, encoding="utf-8")
        outputs.append(str(md))
        res = f"--resource-path={out_dir}{os.pathsep}."
        html = out_dir / f"{base}.html"
        try:
            pypandoc.convert_file(str(md), "html5", format="markdown", outputfile=str(html),
                                  extra_args=["--standalone", "--embed-resources", f"--css={css}", res,
                                              "--metadata", f"pagetitle={title}", "--metadata", "lang=ko"])
            outputs.append(str(html))
        except RuntimeError as e:
            failures.append(f"HTML({kind}): {e}")
            continue
        if not args.no_pdf:
            pdf = out_dir / f"{base}.pdf"
            if html_to_pdf(html, pdf):
                outputs.append(str(pdf))
            else:
                failures.append(f"PDF({kind}): Chrome 인쇄 실패 또는 Chrome 없음")
        if not args.no_docx:
            docx = out_dir / f"{base}.docx"
            try:
                pypandoc.convert_file(str(md), "docx", format="markdown", outputfile=str(docx),
                                      extra_args=[res, f"--reference-doc={ref_docx}"])
                outputs.append(str(docx))
            except RuntimeError as e:
                failures.append(f"DOCX({kind}): {e}")

    report = {"draft": str(draft), "title": title, "figures_used": used, "figures_missing": missing,
              "outputs": outputs, "failures": failures}
    report_path = out_dir / f"{args.name}_build_report.json"
    if report_path.exists() and not args.force:
        report_path = out_dir / f"{args.name}_build_report_{len(list(out_dir.glob(args.name + '_build_report*')))+1}.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.rmtree(tmp, ignore_errors=True)

    print(f"[figures] 삽입 {len(used)}개, 누락 {len(missing)}개" + (f": {', '.join(missing)}" if missing else ""))
    for o in outputs:
        print(f"[output] {o}")
    for f in failures:
        print(f"[fail] {f}", file=sys.stderr)
    print(f"[report] {report_path}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
