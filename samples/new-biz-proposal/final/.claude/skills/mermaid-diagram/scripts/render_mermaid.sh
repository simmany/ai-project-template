#!/usr/bin/env bash
# mermaid(.mmd)를 프로젝트 스타일로 PNG/SVG 렌더링한다. 같은 출력 파일이 있으면 덮어쓰지 않는다.
# 사용: bash .claude/skills/mermaid-diagram/scripts/render_mermaid.sh <input.mmd> <output.png|svg> [width=1600] [scale=3]
set -euo pipefail

in="${1:?입력 .mmd 경로가 필요합니다}"
out="${2:?출력 .png 또는 .svg 경로가 필요합니다}"
width="${3:-1600}"
scale="${4:-3}"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
config="$script_dir/../assets/mermaid-config.json"
cli_version="11.4.2"

[ -f "$in" ] || { echo "입력 파일이 없습니다: $in" >&2; exit 2; }
if [ -e "$out" ]; then
  echo "이미 있는 파일입니다(덮어쓰기 금지): $out — 버전을 올려 다시 실행하세요." >&2
  exit 2
fi
command -v npx >/dev/null 2>&1 || { echo "npx가 없습니다. Node.js를 설치하세요." >&2; exit 2; }
mkdir -p "$(dirname "$out")"

# 시스템 Chrome이 있으면 puppeteer 브라우저 다운로드를 건너뛴다.
pp_dir="$(mktemp -d)"
pp_cfg="$pp_dir/puppeteer.json"
trap 'rm -rf "$pp_dir"' EXIT
chrome=""
for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
         "/Applications/Chromium.app/Contents/MacOS/Chromium" \
         "$(command -v google-chrome 2>/dev/null || true)" \
         "$(command -v chromium 2>/dev/null || true)"; do
  if [ -n "$c" ] && [ -x "$c" ]; then chrome="$c"; break; fi
done
if [ -n "$chrome" ]; then
  printf '{"executablePath":"%s","args":["--no-sandbox"]}' "$chrome" > "$pp_cfg"
  export PUPPETEER_SKIP_DOWNLOAD=1
else
  printf '{"args":["--no-sandbox"]}' > "$pp_cfg"
fi

npx -y "@mermaid-js/mermaid-cli@${cli_version}" \
  -i "$in" -o "$out" -c "$config" -p "$pp_cfg" \
  -w "$width" -s "$scale" -b white

[ -s "$out" ] || { echo "렌더링 결과가 비어 있습니다: $out" >&2; exit 1; }
echo "[rendered] $out"
