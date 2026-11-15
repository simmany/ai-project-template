#!/usr/bin/env bash
# PDF를 페이지별 텍스트로 추출하고, 글자가 적은 페이지는 PNG로 렌더링한다.
# 사용: bash .claude/skills/context-analysis/scripts/extract_pdf.sh <pdf> <outdir> [min_chars=600] [dpi=110]
# 출력: <outdir>/page_NN.txt, (글자 부족 페이지) page_NN.png, summary.tsv
set -euo pipefail

pdf="${1:?PDF 경로가 필요합니다}"
outdir="${2:?출력 폴더가 필요합니다}"
min_chars="${3:-600}"
dpi="${4:-110}"

for cmd in pdfinfo pdftotext pdftoppm; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "필요한 명령이 없습니다: $cmd (brew install poppler)" >&2; exit 2; }
done
[ -f "$pdf" ] || { echo "파일이 없습니다: $pdf" >&2; exit 2; }

mkdir -p "$outdir"
pages=$(pdfinfo "$pdf" | awk '/^Pages:/{print $2}')
printf 'page\tchars\timage\n' > "$outdir/summary.tsv"

for ((i = 1; i <= pages; i++)); do
  nn=$(printf '%02d' "$i")
  pdftotext -f "$i" -l "$i" -layout "$pdf" "$outdir/page_${nn}.txt"
  chars=$(tr -d '[:space:]' < "$outdir/page_${nn}.txt" | wc -m | tr -d ' ')
  image="no"
  if [ "$chars" -lt "$min_chars" ]; then
    pdftoppm -f "$i" -l "$i" -r "$dpi" -png -singlefile "$pdf" "$outdir/page_${nn}"
    image="yes"
  fi
  printf '%s\t%s\t%s\n' "$nn" "$chars" "$image" >> "$outdir/summary.tsv"
done

echo "pages=$pages outdir=$outdir"
column -t -s $'\t' "$outdir/summary.tsv"
