# Flask — 화면의 버튼으로 Python 함수 하나 실행 (대시보드형)

`rules/coding.md`의 기본 기준으로 만들 때 참고하는 예제다. 사용자가 다른 방법을 정한 작업에는 쓰지 않는다.

`app.py`

```python
from flask import Flask, jsonify, request

from clean_notices import clean, parse_csv  # python-script.md 스크립트의 함수를 그대로 쓴다

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
