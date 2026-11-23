# Flask 관리 화면형 — 목록·등록·수정 폼 (Jinja2)

`rules/coding.md`의 기본 기준으로 만들 때 참고하는 예제다. 사용자가 다른 방법을 정한 작업에는 쓰지 않는다.

`sqlite.md`의 DB 함수와 `schema.sql`은 그대로 쓰고, 두 가지를 바꾼다.

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
