# Python 스크립트 — 파일을 넣으면 파일이 나오는 것

`rules/coding.md`의 기본 기준으로 만들 때 참고하는 예제다. 사용자가 다른 방법을 정한 작업에는 쓰지 않는다.

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

- 처리 함수(`parse_csv`, `clean`)와 실행부(`main`)를 나눈다. `flask.md`의 Flask가 이 함수를 그대로 가져다 쓴다.
- 결과 파일은 `output/`에 쓴다. 0행이면 헤더만 있는 파일을 새로 쓰고, 필수 열이 없으면 파일을 쓰지 않고 오류로 끝낸다.
- 비밀 키가 필요한 수집 스크립트도 서버 없이 된다. 키는 `python-env.md`처럼 `.env`에서 읽는다.
