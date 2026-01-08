#!/bin/bash
# Claude Code 리눅스 알림 스크립트
# Usage: notify.sh <type> <message>
#   type: permission, idle, complete
#   message: 표시할 메시지

TYPE="${1:-info}"
MESSAGE="${2:-Claude Code 알림}"

# 아이콘 및 urgency 설정
case "$TYPE" in
  "permission")
    ICON="dialog-warning"
    URGENCY="critical"
    TITLE="Claude Code - 권한 요청"
    ;;
  "idle")
    ICON="dialog-question"
    URGENCY="normal"
    TITLE="Claude Code - 입력 대기"
    ;;
  "complete")
    ICON="dialog-information"
    URGENCY="normal"
    TITLE="Claude Code - 완료"
    ;;
  *)
    ICON="dialog-information"
    URGENCY="low"
    TITLE="Claude Code"
    ;;
esac

# notify-send가 있는지 확인
if command -v notify-send &> /dev/null; then
  notify-send "$TITLE" "$MESSAGE" -u "$URGENCY" -i "$ICON" -t 5000
# macOS의 경우 osascript 사용
elif command -v osascript &> /dev/null; then
  osascript -e "display notification \"$MESSAGE\" with title \"$TITLE\""
fi

exit 0
