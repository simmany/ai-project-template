# Python 실행 환경

`rules/coding.md`의 기본 기준으로 만들 때 참고하는 예제다. 사용자가 다른 방법을 정한 작업에는 쓰지 않는다.

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
