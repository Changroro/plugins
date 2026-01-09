#!/bin/bash
# Claude Code 리눅스 알림 스크립트
# Usage: notify.sh <type> <message>
#   type: permission, idle, complete
#   message: 표시할 메시지

TYPE="${1:-info}"
MESSAGE="${2:-Claude Code 알림}"

# 스크립트 위치 기준으로 아이콘 경로 설정 (절대 경로로 변환)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAWD_ICON="$(realpath "${SCRIPT_DIR}/../assets/clawd.png" 2>/dev/null)"

# 아이콘 및 urgency 설정
case "$TYPE" in
  "permission")
    URGENCY="critical"
    TITLE="Claude Code - 권한 요청"
    ;;
  "idle")
    URGENCY="normal"
    TITLE="Claude Code - 입력 대기"
    ;;
  "complete")
    URGENCY="normal"
    TITLE="Claude Code - 완료"
    ;;
  *)
    URGENCY="low"
    TITLE="Claude Code"
    ;;
esac

# Clawd 아이콘이 없으면 시스템 아이콘 사용
if [[ -f "$CLAWD_ICON" ]]; then
  ICON="$CLAWD_ICON"
else
  ICON="dialog-information"
fi

# notify-send가 있는지 확인
if command -v notify-send &> /dev/null; then
  notify-send "$TITLE" "$MESSAGE" -u "$URGENCY" -i "$ICON" -t 10000
# macOS의 경우 osascript 사용
elif command -v osascript &> /dev/null; then
  osascript -e "display notification \"$MESSAGE\" with title \"$TITLE\""
fi

exit 0
