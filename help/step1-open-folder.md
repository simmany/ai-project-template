# 1단계. 폴더를 에이전트에게 열어 주기

에이전트가 일할 자리를 정해 주는 단계입니다. 내려받은 폴더를 내가 쓰는 AI 에이전트에서 열면 됩니다. AI 에이전트는 하나만 고릅니다.

## 폴더 준비하기

1. 아직 ZIP으로 받지 않았다면 저장소 첫 화면의 초록색 Code 버튼을 누르고 Download ZIP을 고릅니다.
2. 압축을 풉니다. `ai-project-template-main` 폴더가 생깁니다. 릴리스에서 받았다면 `ai-project-template-1.7.2`처럼 버전이 붙은 이름입니다.
3. 그 폴더를 열어 `AGENTS.md` 파일이 바로 보이는지 확인합니다. 같은 이름의 폴더 하나만 들어 있으면 그 안쪽 폴더가 프로젝트 폴더입니다. Windows에서 압축을 풀면 이렇게 되곤 합니다. 안쪽 폴더를 밖으로 꺼내 씁니다.
4. 프로젝트 폴더의 이름을 바꿉니다. 실습은 `교육제안서`라는 이름으로 따라 합니다.
5. 문서 폴더처럼 찾기 쉬운 곳에 둡니다.

실습을 마치고 내 일을 시작할 때는 폴더를 새로 받아 일마다 하나씩 둡니다. 예를 들면 `견적서` 폴더입니다.

## AI 에이전트 고르기

| 종류 | AI 에이전트 | 어울리는 사람 |
| --- | --- | --- |
| 업무 에이전트 | ChatGPT Work, Claude(Cowork) | 앱 화면에서 쓰고 싶은 사람. 처음이라면 여기서 시작합니다 |
| 코딩 에이전트 | Codex, Claude Code | 개발 도구가 익숙한 사람. 문서 일도 맡길 수 있습니다 |

지금 구독하고 있는 서비스(ChatGPT나 Claude)의 AI 에이전트를 고르면 됩니다. 대부분 유료 요금제에서 쓸 수 있습니다.

아래 화면의 이름은 2026년 11월 21일에 각 회사의 안내 문서로 확인한 영어 이름입니다. 화면이 한국어로 보이면 같은 뜻의 이름을 찾습니다. 앱이 바뀌어 이름이 다르면 맨 아래의 공식 안내를 봅니다.

## ChatGPT Work에서 열기

1. ChatGPT 데스크톱 앱을 열고 로그인합니다. 내 컴퓨터의 폴더를 쓰려면 웹 브라우저가 아니라 컴퓨터에 설치하는 앱이 필요합니다. 없으면 https://chatgpt.com/download 에서 Windows용이나 Mac용을 받아 설치합니다.
2. 앱에서 ChatGPT를 고르고, 새 채팅 화면의 입력창 위에서 Work로 바꿉니다.
3. 폴더를 엽니다. 안내 문서는 이 동작을 open a folder라고 적습니다. `교육제안서` 폴더를 고릅니다.
4. 입력창에서 일하는 곳이 내 컴퓨터(Local)인지 확인합니다. 클라우드(Cloud)로 돼 있으면 Local로 바꿉니다. Cloud에서는 내 폴더를 쓰지 못합니다.

일하는 동안에는 앱을 켜 둡니다. 프로젝트로 묶어 두는 방법은 앱의 프로젝트 안내를 따릅니다. 안내 문서에는 프로젝트를 만든 뒤(create a project) 프로젝트 메뉴의 Edit project, Add folder로 폴더를 붙인다고 적혀 있습니다.

## Claude에서 열기 (Cowork)

1. Claude 데스크톱 앱을 열고 로그인합니다. 내 컴퓨터의 폴더를 쓰려면 웹 브라우저가 아니라 컴퓨터에 설치하는 앱이 필요합니다. 없으면 https://claude.com/download 에서 Windows용이나 Mac용을 받아 설치합니다.
2. 입력창에 Chat과 Cowork를 고르는 자리가 보이면 Cowork를 고릅니다. 보이지 않으면 둘이 합쳐진 새 화면이니 그대로 진행합니다.
3. 왼쪽 메뉴의 Projects에서 + 버튼을 누르고 Use an existing folder(이미 있는 폴더 쓰기)를 고릅니다. 이 항목이 보이지 않으면 앱을 최신 버전으로 올립니다.
4. `교육제안서` 폴더를 고르고 프로젝트 이름을 정한 뒤 Create를 누릅니다. 저장 위치나 Instructions 같은 칸이 함께 나오면 필요한 것만 채웁니다.

프로젝트를 만들지 않고 입력창에서 폴더를 바로 추가해도 됩니다. 일하는 동안에는 앱을 켜 둡니다.

## Codex에서 열기

- 앱에서: ChatGPT 데스크톱 앱의 ChatGPT 선택 목록에서 Codex를 고르고, 폴더를 엽니다(open a folder). `교육제안서` 폴더를 고릅니다.
- 터미널에서: 프로젝트 폴더로 이동해 `codex`를 실행합니다.

```
cd "/Users/내이름/Documents/교육제안서"
codex
```

## Claude Code에서 열기

- 앱에서: Claude 데스크톱 앱의 사이드바 맨 위에서 Code 탭을 누릅니다. 입력창 아래 줄에서 Local을 고르고, 그 옆의 폴더 칸에서 Open folder…로 `교육제안서` 폴더를 고릅니다.
- 터미널에서: 프로젝트 폴더로 이동해 `claude`를 실행합니다.

```
cd "/Users/내이름/Documents/교육제안서"
claude
```

처음 열 때 이 폴더를 믿을 수 있는지 물으면 내 폴더이므로 믿는다고 답합니다.

## 확인하기

에이전트에게 아래처럼 물어봅니다.

```
이 폴더에 무엇이 들어 있는지 알려줘.
```

`AGENTS.md`, `rules`, `input`, `workflow`, `output` 같은 이름을 말하면 폴더가 제대로 열린 것입니다. 말하지 않으면 [막혔을 때](troubleshooting.md)의 '폴더를 열 때'를 봅니다.

## 공식 안내

- ChatGPT Work: https://help.openai.com/articles/20001275
- ChatGPT의 프로젝트: https://learn.chatgpt.com/docs/projects
- Claude(Cowork)의 프로젝트: https://support.claude.com/en/articles/14116274-organize-your-tasks-with-projects-in-claude-cowork
- Codex(앱): https://learn.chatgpt.com/docs/quickstart
- Codex(터미널): https://learn.chatgpt.com/docs/cli
- Claude Code(앱): https://code.claude.com/docs/en/desktop-quickstart
- Claude Code(터미널): https://code.claude.com/docs/en/quickstart

다음: [2단계. 첫 요청 보내기](step2-first-request.md)
