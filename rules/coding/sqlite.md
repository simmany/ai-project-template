# SQLite 더하기 — 저장이 필요할 때만

`rules/coding.md`의 기본 기준으로 만들 때 참고하는 예제다. 사용자가 다른 방법을 정한 작업에는 쓰지 않는다.

`db/schema.sql`

```sql
CREATE TABLE IF NOT EXISTS notices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT '접수',
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

`flask.md`에 있는 `app.py`의 `app = Flask(...)` 아래에 DB 함수를 더한다.

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
