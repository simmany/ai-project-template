# HTML 도구 — 한 장으로 끝나는 것

`rules/coding.md`의 기본 기준으로 만들 때 참고하는 예제다. 사용자가 다른 방법을 정한 작업에는 쓰지 않는다.

`index.html` — CSV를 열어 표로 보고, 검색어로 거르고, 결과를 CSV로 내려받는다.

```html
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>CSV 보기·거르기·내려받기</title>
<style>
  body { font-family: sans-serif; margin: 24px; }
  .bar { display: flex; gap: 8px; align-items: center; margin-bottom: 12px; }
  table { border-collapse: collapse; }
  th, td { border: 1px solid #ccc; padding: 4px 8px; }
  th { background: #f3f3f3; }
  #message { color: #b00020; }
</style>
</head>
<body>
  <h1>CSV 보기·거르기·내려받기</h1>
  <div class="bar">
    <input type="file" id="file" accept=".csv">
    <input type="search" id="keyword" placeholder="검색어">
    <button id="download" disabled>결과 CSV 내려받기</button>
    <span id="count"></span>
  </div>
  <p id="message"></p>
  <table id="table"></table>

<script>
let header = [];
let rows = [];

// UTF-8이 아니면 한국어 엑셀 CSV(cp949)로 읽는다
function decode(buffer) {
  try {
    return new TextDecoder("utf-8", { fatal: true }).decode(buffer);
  } catch {
    return new TextDecoder("euc-kr").decode(buffer);
  }
}

// 따옴표 안의 쉼표·줄바꿈까지 처리하는 작은 CSV 파서
function parseCSV(text) {
  const result = [];
  let row = [];
  let field = "";
  let quoted = false;
  text = text.replace(/^\uFEFF/, "");
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') quoted = false;
      else field += c;
    } else if (c === '"') quoted = true;
    else if (c === ",") { row.push(field); field = ""; }
    else if (c === "\n") { row.push(field); result.push(row); row = []; field = ""; }
    else if (c !== "\r") field += c;
  }
  if (field !== "" || row.length > 0) { row.push(field); result.push(row); }
  return result;
}

function toCSV(data) {
  const cell = (v) => (/[",\r\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v);
  return data.map((r) => r.map(cell).join(",")).join("\r\n");
}

function filtered() {
  const keyword = document.querySelector("#keyword").value.trim();
  return keyword ? rows.filter((r) => r.some((v) => v.includes(keyword))) : rows;
}

function makeRow(values, tag) {
  const tr = document.createElement("tr");
  for (const v of values) {
    const cell = document.createElement(tag);
    cell.textContent = v; // 데이터는 textContent로 넣는다
    tr.append(cell);
  }
  return tr;
}

function render() {
  const visible = filtered();
  const table = document.querySelector("#table");
  if (header.length === 0) {
    table.replaceChildren();
    document.querySelector("#count").textContent = "";
    return;
  }
  table.replaceChildren(makeRow(header, "th"), ...visible.map((r) => makeRow(r, "td")));
  document.querySelector("#count").textContent = `${visible.length} / ${rows.length}행`;
}

document.querySelector("#file").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  const data = parseCSV(decode(await file.arrayBuffer()));
  // 새 파일을 열면 이전 내용은 지운다
  [header = [], ...rows] = data;
  document.querySelector("#message").textContent = data.length === 0 ? "빈 파일입니다." : "";
  document.querySelector("#download").disabled = data.length === 0;
  render();
});

document.querySelector("#keyword").addEventListener("input", render);

document.querySelector("#download").addEventListener("click", () => {
  // 맨 앞의 \uFEFF(BOM)는 엑셀에서 한글이 깨지지 않게 한다
  const csv = "\uFEFF" + toCSV([header, ...filtered()]);
  const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = "result.csv";
  a.click();
  URL.revokeObjectURL(url);
});
</script>
</body>
</html>
```

- 파일을 더블클릭하면 서버 없이 열린다. 외부 JS 라이브러리가 필요하면 CDN 대신 `vendor/`에 파일로 받아 둔다 (사내망 대비).
- 내려받은 CSV는 브라우저의 다운로드 폴더로 간다. 프로젝트의 `output/`에 자동으로 저장되지 않는다.
- 페이지가 `fetch()`로 데이터 파일을 읽어야 하면 페이지와 데이터 파일을 `static/`에 두고 아래처럼 연다. 앱 폴더 전체를 열면 `.env`와 `db/`까지 보이므로 그렇게 열지 않는다.

```
python -m http.server 8000 --bind 127.0.0.1 --directory static
```
