# 코딩 뼈대 (Coding Skeleton)

`rules/coding.md`의 기본 기준으로 만들 때 쓴다.
**1절 앱 폴더 구조와 이름은 따른다. 2절부터의 예제는 지금 필요한 것만 골라 참고한다.**
사용자가 다른 방법을 정한 작업에는 쓰지 않고, 다른 기술을 쓰면 그 기술에 해당하지 않는 절은 보지 않는다.

## 1. 앱 폴더 구조 (따른다)

```
codebase/<앱이름>/
├── README.md         첫 줄: 종류(HTML 도구 / 스크립트 / Flask 대시보드형 / Flask 관리 화면형)와 한 줄 설명
├── index.html        HTML 도구 (CSS·JS를 안에 넣은 한 장)
├── <작업이름>.py      Python 스크립트 (예: clean_notices.py)
├── app.py            Flask 서버
├── static/           서버가 브라우저에 주는 화면 파일 (index.html, 필요하면 app.js·style.css, vendor/)
├── templates/        Flask 관리 화면형의 Jinja2 템플릿
├── db/               SQLite를 쓸 때만: schema.sql, app.db
├── requirements.txt  외부 패키지를 쓸 때 (설치한 버전 기록)
├── .env              비밀값이 있을 때 (git 제외)
└── .gitignore
```

- 필요한 것만 만든다. 만드는 것의 이름과 위치는 위와 같게 한다.
- 명령은 앱 폴더(`codebase/<앱이름>/`)에서 실행한다. 그래서 `input/`, `output/`은 `../../input/`, `../../output/`이 된다.
- 명령의 `python`은 macOS에서 가상환경 밖이라면 `python3`로 쓴다.

README 예:

```
Flask 대시보드형 — 공고 CSV를 올리면 제목을 정리해 보여 준다

실행
  cd codebase/notice-cleaner
  source .venv/bin/activate
  python app.py
접속: http://127.0.0.1:5001
```

## 2. HTML 도구 — 한 장으로 끝나는 것

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

## 3. Python 스크립트 — 파일을 넣으면 파일이 나오는 것

`clean_notices.py` — 제목이 빈 행을 빼고 제목 앞뒤 공백을 정리한다.

```python
"""공고 CSV에서 제목이 빈 행을 빼고 제목 앞뒤 공백을 정리해 저장한다.

실행: python clean_notices.py ../../input/notices.csv ../../output/notices_clean.csv
"""
import csv
import io
import sys
from pathlib import Path

REQUIRED_COLUMNS = ["title"]


def decode(raw):
    """UTF-8이 아니면 한국어 엑셀 CSV(cp949)로 읽는다."""
    for encoding in ("utf-8-sig", "cp949"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("파일 인코딩을 알 수 없습니다")


def parse_csv(raw):
    """CSV 바이트를 (열 이름 목록, 행 목록)으로 바꾼다. Flask에서도 쓴다."""
    reader = csv.DictReader(io.StringIO(decode(raw)))
    return reader.fieldnames or [], list(reader)


def clean(fieldnames, rows):
    """실제 처리. Flask에서도 이 함수를 그대로 가져다 쓴다."""
    missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
    if missing:
        raise ValueError(f"필수 열이 없습니다: {', '.join(missing)}")
    result = []
    for row in rows:
        title = (row.get("title") or "").strip()
        if title:
            result.append({**row, "title": title})
    return result


def write_csv(path, fieldnames, rows):
    # 0행이어도 헤더만 있는 새 파일을 써서 이전 결과가 남지 않게 한다
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main(src, dst):
    fieldnames, rows = parse_csv(Path(src).read_bytes())
    result = clean(fieldnames, rows)
    write_csv(dst, fieldnames, result)
    print(f"{len(result)}행 저장: {dst}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("사용법: python clean_notices.py <입력.csv> <출력.csv>")
        sys.exit(1)
    try:
        main(sys.argv[1], sys.argv[2])
    except ValueError as e:
        print(f"오류: {e}")
        sys.exit(1)
```

- 처리 함수(`parse_csv`, `clean`)와 실행부(`main`)를 나눈다. 4절의 Flask가 이 함수를 그대로 가져다 쓴다.
- 결과 파일은 `output/`에 쓴다. 0행이면 헤더만 있는 파일을 새로 쓰고, 필수 열이 없으면 파일을 쓰지 않고 오류로 끝낸다.
- 비밀 키가 필요한 수집 스크립트도 서버 없이 된다. 키는 7절처럼 `.env`에서 읽는다.

## 4. Flask — 화면의 버튼으로 Python 함수 하나 실행 (대시보드형)

`app.py`

```python
from flask import Flask, jsonify, request

from clean_notices import clean, parse_csv  # 3절 스크립트의 함수를 그대로 쓴다

# static/ 폴더 안의 파일만 브라우저에 준다 (.env, db/는 보이지 않는다)
app = Flask(__name__, static_folder="static", static_url_path="")
app.json.ensure_ascii = False  # JSON 응답의 한글을 \uXXXX 대신 그대로 보이게


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.post("/api/clean")
def run_clean():
    file = request.files.get("file")
    if file is None:
        return jsonify(error="CSV 파일을 골라 주세요"), 400
    try:
        fieldnames, rows = parse_csv(file.read())
        result = clean(fieldnames, rows)
    except ValueError as e:
        return jsonify(error=str(e)), 400
    return jsonify(count=len(result), rows=result)


if __name__ == "__main__":
    # macOS는 5000번을 AirPlay 수신이 쓰므로 5001번을 쓴다
    app.run(host="127.0.0.1", port=5001, debug=True)
```

`static/index.html`

```html
<!doctype html>
<html lang="ko">
<head><meta charset="utf-8"><title>공고 정리</title></head>
<body>
  <h1>공고 정리</h1>
  <input type="file" id="file" accept=".csv">
  <button id="run">정리하기</button>
  <p id="message"></p>
  <ul id="list"></ul>

<script>
document.querySelector("#run").addEventListener("click", async () => {
  const message = document.querySelector("#message");
  const list = document.querySelector("#list");
  list.replaceChildren();
  const file = document.querySelector("#file").files[0];
  if (!file) {
    message.textContent = "CSV 파일을 골라 주세요";
    return;
  }
  const form = new FormData();
  form.append("file", file);
  const res = await fetch("/api/clean", { method: "POST", body: form });
  const data = await res.json();
  if (!res.ok) {
    message.textContent = data.error;
    return;
  }
  message.textContent = `${data.count}행 정리됨`;
  list.replaceChildren(...data.rows.map((row) => {
    const li = document.createElement("li");
    li.textContent = row.title; // 데이터는 textContent로 넣는다
    return li;
  }));
});
</script>
</body>
</html>
```

- API 주소는 `/api/` + 이름으로 짓고, 오류는 `{"error": "메시지"}`와 상태 코드(400, 404)로 돌려준다.
- 공용 비밀 키로 외부 API를 불러야 할 때도 같은 모양이다. 라우트 안에서 `os.environ`으로 키를 읽어 호출하고, 브라우저에는 결과만 돌려준다.
- 서버 없이 JSON 파일을 읽던 화면을 옮길 때는 `fetch` 주소만 바꾼다: `data/notices.json` → `/api/notices`

## 5. SQLite 더하기 — 저장이 필요할 때만

`db/schema.sql`

```sql
CREATE TABLE IF NOT EXISTS notices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT '접수',
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

4절 `app.py`의 `app = Flask(...)` 아래에 DB 함수를 더한다.

```python
import os
import sqlite3

from flask import g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "app.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "db", "schema.sql")
STATUSES = ["접수", "검토중", "완료"]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.close()


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()
```

조회·등록·상태 수정 API. SQL 값은 반드시 `?` 자리에 넘긴다.

```python
@app.get("/api/notices")
def list_notices():
    rows = db().execute("SELECT * FROM notices ORDER BY id DESC").fetchall()
    return jsonify([dict(r) for r in rows])


@app.post("/api/notices")
def create_notice():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify(error="title 값이 필요합니다"), 400
    cur = db().execute("INSERT INTO notices (title) VALUES (?)", (title,))
    db().commit()
    return jsonify(id=cur.lastrowid), 201


@app.patch("/api/notices/<int:notice_id>")
def update_notice(notice_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in STATUSES:
        return jsonify(error=f"status는 {', '.join(STATUSES)} 중 하나여야 합니다"), 400
    cur = db().execute(
        "UPDATE notices SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (status, notice_id),
    )
    db().commit()
    if cur.rowcount == 0:
        return jsonify(error="없는 공고입니다"), 404
    return jsonify(ok=True)
```

실행부에서 서버를 켜기 전에 DB를 준비한다.

```python
if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5001, debug=True)
```

- 스크립트에서 SQLite를 쓸 때도 같다. `sqlite3.connect("db/app.db")`로 열고, 값은 `?` 자리에 넘긴다.

## 6. Flask 관리 화면형 — 목록·등록·수정 폼 (Jinja2)

5절의 DB 함수와 `schema.sql`은 그대로 쓰고, 두 가지를 바꾼다.

1. `app = Flask(__name__)` — static 설정은 기본값으로 둔다
2. JSON 대신 화면과 폼 처리 라우트를 쓴다

```python
from flask import redirect, render_template, request, url_for


@app.get("/")
def notice_list():
    notices = db().execute("SELECT * FROM notices ORDER BY id DESC").fetchall()
    return render_template("notices.html", notices=notices, statuses=STATUSES)


@app.post("/notices")
def notice_create():
    title = request.form.get("title", "").strip()
    if not title:
        return "공고 제목이 필요합니다", 400
    db().execute("INSERT INTO notices (title) VALUES (?)", (title,))
    db().commit()
    return redirect(url_for("notice_list"))


@app.post("/notices/<int:notice_id>/status")
def notice_status(notice_id):
    status = request.form.get("status")
    if status not in STATUSES:
        return "잘못된 상태 값입니다", 400
    db().execute(
        "UPDATE notices SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (status, notice_id),
    )
    db().commit()
    return redirect(url_for("notice_list"))
```

`templates/notices.html` — `{{ }}` 값은 Jinja2가 자동으로 안전하게 바꿔 넣는다.

```html
<!doctype html>
<html lang="ko">
<head><meta charset="utf-8"><title>공고 관리</title></head>
<body>
  <h1>공고 관리</h1>
  <form method="post" action="{{ url_for('notice_create') }}">
    <input name="title" placeholder="공고 제목" required>
    <button>등록</button>
  </form>
  <table>
    <tr><th>제목</th><th>상태</th></tr>
    {% for notice in notices %}
    <tr>
      <td>{{ notice.title }}</td>
      <td>
        <form method="post" action="{{ url_for('notice_status', notice_id=notice.id) }}">
          <select name="status">
            {% for s in statuses %}
            <option {% if s == notice.status %}selected{% endif %}>{{ s }}</option>
            {% endfor %}
          </select>
          <button>저장</button>
        </form>
      </td>
    </tr>
    {% endfor %}
  </table>
</body>
</html>
```

- 차트만 새로 그리는 식의 부분 갱신이 필요하면 그 부분에만 `fetch()`와 JSON 라우트를 더한다. 목록 자체는 Jinja2로만 그린다.

## 7. Python 실행 환경

```
cd codebase/<앱이름>
python -m venv .venv
source .venv/bin/activate        # macOS
.venv\Scripts\activate           # Windows
pip install flask                # 필요한 패키지만
pip freeze > requirements.txt    # 설치한 버전을 기록한다
python app.py                    # → http://127.0.0.1:5001
```

- 다시 설치할 때는 `pip install -r requirements.txt`
- 표준 라이브러리만 쓰는 스크립트는 가상환경 없이 실행해도 된다.

비밀값은 `.env`에 두고 읽는다 (`pip install python-dotenv`).

```
API_KEY=여기에-키
```

```python
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ["API_KEY"]
```

`.gitignore`

```
.env
.venv/
db/*.db
__pycache__/
```
