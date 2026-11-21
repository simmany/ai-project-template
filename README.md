# ai-project-template

AI 에이전트에게 일을 맡길 때 쓰는 작업 폴더입니다. 에이전트는 대화만 하는 챗봇과 달리, 내 폴더의 파일을 읽고 만들면서 일을 해 주는 AI입니다. 이 폴더에는 일하는 법(`AGENTS.md`)과 다섯 개의 자리가 들어 있어서, 에이전트에게 폴더를 열어 주면 같은 규칙으로 일하고 기록을 남깁니다. 개발자가 아니어도 쓸 수 있습니다.

## 시작하기

1. 받기: [저장소](https://github.com/simmany/ai-project-template) 첫 화면의 초록색 **Code** 버튼을 누르고 **Download ZIP**을 고릅니다([바로 받기](https://github.com/simmany/ai-project-template/archive/refs/heads/main.zip)). 압축을 풀고, `AGENTS.md`가 바로 보이는 폴더의 이름을 내 프로젝트 이름으로 바꿉니다. `git clone`으로 받아도 내용은 같습니다.
2. 열기: ChatGPT Work, Claude, Codex, Claude Code 가운데 쓰는 제품에서 이 폴더를 엽니다. 방법은 [1단계](help/step1-open-folder.md)에 있습니다.
3. 맡기기: 아래처럼 보냅니다. 괄호 자리에 맡길 일을 적습니다.

```
AGENTS.md를 먼저 읽고, (맡길 일)을 진행해줘.
```

일이 끝나면 폴더를 봅니다. `workflow/`에 요청과 응답의 기록이, `output/`에 결과물이, `_workspace/memory/status.md`에 지금 상태가 남습니다.

일 하나에 폴더 하나를 씁니다. 다른 일을 시작할 때는 폴더를 새로 받습니다.

## 단계별 안내

처음이라면 `help/` 폴더의 안내를 1단계부터 따라 합니다. '교육 제안서'라는 예제로 해 보는 실습이고, 한 번에 다 하지 않아도 됩니다. 2단계까지만 해도 쓸 수 있습니다. 7단계는 비서 에이전트를 쓰는 사람만 합니다.

| 단계 | 하는 일 |
| --- | --- |
| [1단계](help/step1-open-folder.md) | 폴더를 에이전트에게 열어 주기 |
| [2단계](help/step2-first-request.md) | 첫 요청 보내기 |
| [3단계](help/step3-input.md) | 참고 자료를 `input/`에 넣기 |
| [4단계](help/step4-rules.md) | 지켜야 할 규칙을 `rules/`에 두기 |
| [5단계](help/step5-workflow.md) | `workflow/`에서 요청과 기록 보기 |
| [6단계](help/step6-context-memory.md) | Context와 Memory 구분하기 |
| [7단계](help/step7-personal-agent.md) | 비서 에이전트가 이 폴더를 읽게 하기 |

안내는 GitHub 화면(github.com/simmany/ai-project-template)에서 읽으면 표와 링크가 제대로 보입니다. 받은 폴더의 파일을 메모장(Windows)이나 텍스트 편집기(Mac)로 열어도 내용은 같습니다. 이름이 `.md`로 끝나는 파일은 글자만 든 문서이고, `#`은 제목, `-`는 목록을 나타내는 표시입니다.

막히면 [막혔을 때](help/troubleshooting.md)를 봅니다. 폴더를 연 뒤에는 에이전트에게 "help 폴더의 안내를 읽고, 내가 지금 무엇을 하면 되는지 알려줘."라고 물어도 됩니다.

## 폴더 구성

```
내 프로젝트/
├── AGENTS.md            일하는 법. 에이전트가 읽습니다
├── CLAUDE.md            Claude Code가 AGENTS.md를 읽게 하는 파일
├── PERSONAL-AGENT.md    비서 에이전트용 규칙 (7단계)
├── rules/               지켜야 할 규칙. 내가 정합니다
├── input/               참고 자료. 내가 넣습니다
├── workflow/            요청과 응답의 기록
├── output/              결과물. AI가 만듭니다
├── _workspace/          AI의 작업 공간과 기록
├── help/                단계별 안내
├── README.md            이 파일
└── LICENSE
```

`help/`, `README.md`, `LICENSE`는 템플릿의 안내와 라이선스입니다. 익숙해지면 지워도 됩니다. 이 폴더를 다른 사람에게 다시 나눠 줄 때는 `LICENSE`를 남겨 둡니다.

## 버전과 라이선스

- 지금 버전은 v1.7입니다. 바뀐 내용은 [릴리스](https://github.com/simmany/ai-project-template/releases)에 있습니다.
- 예전 폴더 구성으로 만든 샘플 프로젝트는 [v1.6 시점의 저장소](https://github.com/simmany/ai-project-template/tree/v1.6/samples)에서 볼 수 있습니다.
- MIT 라이선스입니다. 전문은 [LICENSE](LICENSE)에 있습니다. 저작권자: Su-Ho Yoo
