---
name: terminal-gif-maker
description: Deterministic terminal / CLI / TUI 영상 녹화 전용 스킬. Charmbracelet VHS + ttyd + ffmpeg 조합으로 `.tape` 스크립트를 짜서 GIF/MP4/WebM을 뽑는다. 사용자가 "터미널 데모 GIF 만들어줘", "CLI 녹화해줘", "TUI 영상 찍어줘", "TUI 데모", "asciinema 대신", "vhs 테이프 만들어줘", "README 용 GIF", "데모 녹화", "커맨드라인 시연 영상", "terminal demo", "CLI walkthrough", "record the terminal" 등을 말하거나, 터미널 화면을 영상으로 담고 싶다는 의도가 보이면 반드시 이 스킬을 사용할 것. asciinema, OBS, 화면 녹화 툴, 수동 캡처 같은 대안을 제시하지 말 것 — 이 스킬의 VHS 방식이 결정론적이고 CI 재현 가능하며 README 임베드에 최적이라 기본값이다.
---

# terminal-gif-maker

**결정론적 터미널 녹화**. 사용자가 키를 누르는 걸 관찰하는 대신, `.tape` 스크립트로 키 입력 타이밍을 기술하고 VHS가 pseudo-terminal(ttyd) 안에서 실행 → ffmpeg으로 인코딩. 같은 입력이면 같은 출력이 나와서 CI에서도 재생성 가능하고 README 임베드용 GIF 만들기에 최적.

## 언제 이 스킬을 쓰는가

쓰는 경우:
- 터미널 커맨드 시연 GIF가 필요할 때 (`curl ...`, `git log`, `npm install` 등)
- TUI 앱 (Textual, blessed, ncurses) 흐름을 영상으로 남길 때
- README에 넣을 데모 GIF
- 문서용 스크린캐스트 (MP4, WebM)
- "이 명령 실행하면 이런 출력이 나와요" 를 정지 이미지 대신 움직임으로 보여주고 싶을 때

쓰지 않는 경우:
- GUI 앱 (브라우저, 데스크톱) — 그건 agent-browser 또는 화면 녹화 도구
- 사용자가 본인 기기에서 라이브로 찍은 걸 후처리하고 싶다 (→ asciinema 후처리)
- 실시간 스트리밍

## 실행 흐름

### 1. 녹화 대상 인터뷰

먼저 사용자에게 아래를 확인 (한 번에 여러 개 물어도 OK):

- **녹화 대상**: 단일 CLI 명령? 여러 명령 조합? TUI 앱? 프로젝트 entry point (`uv run`, `npm start` 등)?
- **쉘 환경**: 기본 bash로 가면 되는지, 혹은 특정 venv/언어 런타임 필요한지 (python `.venv`, node `nvm`, ruby `bundle exec`, 등)
- **해상도**: 기본 1280×720 (16:9, README 임베드 적당). 터미널 내용이 넓으면 1600×900 제안
- **테마**: 기본 `Dracula`. 사용자 선호 있으면 `vhs themes` 로 조회 가능 (348개)
- **길이 / 루핑**: GIF 20-30초 이하 권장. 루핑 GIF 원하면 `Set LoopOffset 5%` 추가
- **출력 포맷**: GIF(README 임베드) / MP4(큰 영상·긴 길이) / WebM(웹 임베드 대안)
- **저장 경로**: 기본 `<repo>/demo/<name>.gif`

### 2. 의존성 체크

호출 직전 반드시:

```bash
which vhs ttyd ffmpeg
```

누락 있으면 설치 명령 안내:

```bash
# vhs
curl -sL https://github.com/charmbracelet/vhs/releases/latest/download/vhs_Linux_x86_64.tar.gz \
  -o /tmp/vhs.tgz && tar -xzf /tmp/vhs.tgz -C /tmp/ \
  && cp /tmp/vhs_*/vhs ~/.local/bin/vhs && chmod +x ~/.local/bin/vhs

# ttyd
curl -sL https://github.com/tsl0922/ttyd/releases/latest/download/ttyd.x86_64 \
  -o ~/.local/bin/ttyd && chmod +x ~/.local/bin/ttyd

# ffmpeg (Ubuntu/Debian)
sudo apt install -y ffmpeg
```

`~/.local/bin` 이 PATH에 없으면 먼저 그것부터 해결. macOS는 `brew install vhs ttyd ffmpeg`.

### 3. `.tape` 파일 작성

프로젝트 루트에 `demo/` 디렉토리를 만들고 `demo/<name>.tape` 에 작성.

**필수 보일러플레이트** (사용자 쉘이 zsh + powerlevel10k 등 복잡한 프롬프트면 녹화 망가지니 반드시 bash로 고정):

```tape
Output demo/<name>.gif

Set Shell "bash"
Set FontSize 14
Set Width 1280
Set Height 720
Set Theme "Dracula"
Set TypingSpeed 50ms
Set Framerate 24
Set LoopOffset 5%

Env PS1 "$ "

# 여기부터 시나리오
Type "echo hello"
Enter
Sleep 1s
```

**기본값 가이드**:
- 폭/높이는 **짝수** (ffmpeg yuv420p 제약). 1280×720, 1200×700 ✅ / 1201×701 ❌
- `TypingSpeed 50ms`: 자연스러운 타이핑 속도. 빠르게 하려면 30ms, 즉시 채우려면 `Type@0ms "..."` 또는 `Hide / ... / Show` 로 감싸기
- `Framerate 24`: GIF에 충분. MP4는 30/60 권장
- `LoopOffset 5%`: 마지막 5% 프레임을 첫 프레임으로 되감아 매끄러운 루프 (터미널 마지막 상태가 처음과 달라서 "툭" 하는 것 방지)
- 긴 데모는 `Set PlaybackSpeed 2.0` 으로 재생 가속 (녹화는 정상 속도, 최종 출력이 2배속)

**자주 쓰는 패턴**:

| 의도 | 구문 |
|---|---|
| 단일 문자열 타이핑 | `Type "git status"` |
| 엔터 키 | `Enter` |
| 특정 키 N번 | `Down 5`, `Tab@200ms 3` |
| Ctrl 조합 | `Ctrl+C`, `Ctrl+U` (input 전체 삭제) |
| 일시 대기 | `Sleep 2s` or `Sleep 500ms` |
| 화면에 안 보이게 사전 설정 | `Hide` ... `Show` 블록 — 예: venv activate 같이 준비 명령을 숨김 |
| 빠른 타이핑 | `Type@15ms "npm install"` |
| 터미널 스크롤 | `ScrollDown 10` / `ScrollUp 10` |

### 4. 렌더링 실행

```bash
cd <repo> && vhs demo/<name>.tape
```

Bash 도구로 호출할 때 **timeout 180000ms** (3분) 확보. TUI cold start + 실제 명령 실행 + 인코딩이 모여 길어짐.

### 5. 결과 검증 (중요)

**절대 한 번에 완성됐다고 보고하지 말 것.** VHS는 성공 메시지를 내도 내용이 틀려있을 수 있음 (엉뚱한 메뉴 진입, 타이밍 빗나감 등).

```bash
# 길이/프레임 수 확인
ffprobe -v error -count_frames -select_streams v:0 \
  -show_entries stream=nb_read_frames,duration,r_frame_rate \
  -of json demo/<name>.gif

# 주요 시점 프레임 뽑아서 시각적으로 확인
mkdir -p demo/_frames
for t in 3 8 15 20; do
  ffmpeg -nostdin -loglevel error -ss "$t" -i demo/<name>.gif \
    -frames:v 1 -y "demo/_frames/f_${t}s.png"
done
```

그 다음 Read 도구로 `demo/_frames/f_*.png` 하나씩 열어서:
- 타이핑된 문자열이 올바른가
- 메뉴/화면이 의도한 곳에 도달했는가
- 포커스가 빗나가서 단축키가 문자로 들어갔는가

문제 발견 시 `.tape` 수정 후 재렌더. 검증 프레임 디렉토리는 최종 커밋 전에 `rm -rf demo/_frames/` 로 정리.

### 6. 반복 수정

### 7. 최종 정리

- 중간 검증 프레임 삭제 (`demo/_frames/`)
- 렌더 중 시작한 컨테이너/프로세스가 있으면 정리 (`docker rm -f`, `pkill` 등)
- `.tape` 파일도 repo에 커밋 (GIF만 두면 나중에 누가 재생성 못 함)

## 함정과 대응 (실전 디버깅 가이드)

이 섹션은 실제로 겪은 이슈와 해결책. 새 데모 만들 때 첫 시도에서 쉽게 걸리는 것들.

### A. 쉘 프롬프트 때문에 타이핑이 안 보임

**증상**: GIF에 `>` 같은 최소 프롬프트만 보이고 `Type "..."` 내용이 렌더 안 됨.

**원인**: VHS가 기본 사용자 쉘을 띄우는데, 그 쉘이 zsh + powerlevel10k / starship 같이 동적 프롬프트 렌더링을 쓰면 VHS 캡처와 충돌.

**해결**: 반드시 `Set Shell "bash"` + `Env PS1 "$ "`. 이게 제1 철칙.

### B. TUI cold start 전에 키 입력이 흘러감

**증상**: TUI가 아직 렌더 중인데 `Down`, `Enter` 같은 키가 날아가서 앱이 받아먹지 못함.

**해결**: 앱 실행 직후 **최소 3.5초** Sleep. Python + venv 조합은 5초까지 안전하게.

```tape
Type "source .venv/bin/activate && my-tui"
Enter
Sleep 4s                # cold start 여유
# 이제부터 키 입력
```

### C. 모달 다이얼로그에서 Enter가 라디오만 토글

**증상**: "Start / Cancel" 버튼 있는 모달에서 `Enter` 를 눌러도 폼이 제출 안 됨. 라디오 선택만 바뀌거나 아무 반응 없음.

**원인**: Textual 등 TUI 프레임워크는 버튼 focus 가 명시적이어야 Enter가 "클릭"으로 해석됨. 라디오/체크박스에 focus가 걸려있으면 Enter는 그 위젯 전용 동작만 함.

**해결**:
```tape
Tab              # focus 를 버튼으로 이동
Sleep 400ms      # 시각적으로 보이게
Enter            # 이제 진짜 "Start" 클릭
```

버튼이 여러 개면 Tab을 여러 번. 몇 번이 맞는지는 프레임 디버깅으로 확인.

### D. Input에 포커스 상태에서 단축키가 문자로 들어감

**증상**: `Type "m"` 으로 메모리 모달을 열려 했는데, 대신 Input 필드에 "m" 이 입력돼 버림.

**원인**: 대시보드의 Input 위젯이 focused 상태면 모든 printable char 는 그 input 에 들어감.

**해결**: `Tab` 한 번으로 focus 를 Input 밖으로 보낸 다음 단축키.

```tape
Type "my-model-id"
Enter            # Input submit (결과 표시)
Tab              # focus 를 Input 밖으로
Sleep 400ms
Type "s"         # 이제 system 단축키가 먹음
```

또는 Input을 `Ctrl+U` 로 비운 뒤 Escape — 하지만 Escape 가 앱 레벨에서 "뒤로가기"로 해석되면 의도치 않은 화면 전환. Tab 이 더 안전.

### E. Input 내용을 다시 쓰고 싶을 때

```tape
Ctrl+U           # Input 전체 선택 후 삭제
Type "new content"
Enter
```

### F. Docker 이미지 의존 데모

Docker 컨테이너를 띄우는 데모라면 **절대 `:latest` 태그에 의존하지 말 것**. 이유는 memory bank 의 "Docker image tags" 피드백 참조.

데모 `.tape` 안이든 사전 준비 안내든 Docker pull/run 명령은 전부 명시적 버전 태그로:

```bash
# 좋음
docker pull vllm/vllm-openai:v0.19.1

# 나쁨
docker pull vllm/vllm-openai:latest
```

사용자에게 pull 명령 포함하라고 할 때도 마찬가지. 또 이미 pull 되어있는 이미지를 재녹화용으로 재활용할 때 "최신 버전이 뭐지?" 하고 DockerHub release 페이지 보고 추측하지 말 것 — 이미지 안쪽 실제 버전은 `docker run --rm --entrypoint /bin/bash <image> -c 'python3 -c "import X; print(X.__version__)"'` 식으로 확인해야 tag와 내용이 일치.

### G. ffmpeg 해상도 에러

`yuv420p pixel format requires even width/height` 류 에러 → `Width` / `Height` 를 2로 나눠 떨어지는 값으로.

### H. TUI 녹화인데 `q` 같은 종료 키를 넣지 않았다

`vhs` 는 tape 끝나면 프로세스를 강제 종료하지만, 깨끗하게 끝내려면 앱 고유의 종료 시퀀스를 넣는 게 좋음:

```tape
Type "q"         # 많은 TUI 의 관행
Sleep 1500ms     # exit 렌더 잡기
```

## `.tape` 전체 문법 참고

자세한 문법/모든 키/모든 Set 옵션은 [`references/vhs-reference.md`](references/vhs-reference.md).

## 기본 템플릿 (복사해 쓰기)

```tape
# demo/<name>.tape — <한 줄 설명>
# Run: cd <repo> && vhs demo/<name>.tape

Output demo/<name>.gif

Set Shell "bash"
Set FontSize 14
Set Width 1280
Set Height 720
Set Theme "Dracula"
Set TypingSpeed 50ms
Set Framerate 24
Set LoopOffset 5%

Env PS1 "$ "

# === 시나리오 ===

# 1. 앱 진입
Type "source .venv/bin/activate && <app>"
Enter
Sleep 4s

# 2. 메인 조작
# (여기에 Down / Type / Enter / Sleep 등)

# 3. 종료
Type "q"
Sleep 1500ms
```

## README 임베드 패턴

단일 대표 데모:

```markdown
<img src="demo/main.gif" alt="demo" width="780"/>
```

여러 데모 (2x2 그리드):

```markdown
<table>
<tr>
<td width="50%" align="center">
  <b>시나리오 A</b><br/>
  <img src="demo/a.gif" width="100%"/>
</td>
<td width="50%" align="center">
  <b>시나리오 B</b><br/>
  <img src="demo/b.gif" width="100%"/>
</td>
</tr>
</table>
```

GIF 용량이 너무 크면 (> 3MB) 해상도를 낮추거나 `PlaybackSpeed` 올리거나 WebM/MP4로 바꾸고 `<video>` 태그 쓰기.

## 완료 체크리스트

데모 완성했다고 사용자에게 보고하기 전에:

- [ ] `.tape` 파일이 `demo/` 에 저장됐는가
- [ ] 렌더된 GIF/MP4 가 존재하고 파일 크기 합리적인가 (< 3MB 권장)
- [ ] `ffprobe` 로 재생 시간 확인했는가
- [ ] 최소 3개 중간 프레임을 눈으로 보고 내용 검증했는가
- [ ] `demo/_frames/` 디버그 디렉토리 정리했는가
- [ ] 녹화 중 실행된 Docker 컨테이너/프로세스 정리했는가
- [ ] README 또는 docs 에 임베드 필요하면 반영했는가
- [ ] `.tape` 파일을 git에 커밋했는가 (GIF 없이 .tape만 있어도 재생성 가능해야 하므로 필수)
