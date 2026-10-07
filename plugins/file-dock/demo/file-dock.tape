# file-dock 데모: Claude가 말한 경로와 내가 적은 경로를 입력창 위 버튼으로 모아 바로 연다
Output demo/file-dock.gif
Set Shell "bash"
Set FontSize 17
Set Width 1280
Set Height 760
Set Theme "Dracula"
Set TypingSpeed 45ms
Set Framerate 20
Set LoopOffset 5%
Env PS1 "$ "

Hide
Type "unset $(compgen -e | grep '^CLAUDE'); export HOME=/tmp/fd-demo/home PATH=/tmp/fd-demo/bin:$PATH && cd /tmp/fd-demo/workspace && clear"
Enter
Sleep 500ms
Show

Type "claude --plugin-dir ../file-dock --model haiku"
Enter
Sleep 7s
Type "notes/CHANGELOG.md 포함해서 이 폴더 자료들 경로를 짧게 정리해줘"
Sleep 600ms
Enter
Sleep 3s
Hide
Sleep 22s
Show
Sleep 2s
Ctrl+X
Tab
Sleep 1200ms
Right
Sleep 700ms
Right
Sleep 900ms
Enter
Sleep 2500ms
Right
Sleep 700ms
Right
Sleep 900ms
Enter
Sleep 3500ms
