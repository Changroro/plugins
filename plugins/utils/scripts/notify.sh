#!/bin/bash
# Claude Code 알림 스크립트 (Linux & macOS)
# Usage: notify.sh <type> <message>
#   type: permission, idle, complete
#   message: 표시할 메시지

TYPE="${1:-info}"
MESSAGE="${2:-Claude Code 알림}"

# 스크립트 위치 기준으로 아이콘 경로 설정 (절대 경로로 변환)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAWD_ICON="$(realpath "${SCRIPT_DIR}/../assets/clawd.png" 2>/dev/null)"

# 타입별 설정
case "$TYPE" in
  "permission")
    URGENCY="normal"
    TITLE="Claude Code - 권한 요청"
    SOUND="Basso"  # macOS 경고음
    ;;
  "idle")
    URGENCY="normal"
    TITLE="Claude Code - 입력 대기"
    SOUND="Blow"   # macOS 알림음
    ;;
  "complete")
    URGENCY="normal"
    TITLE="Claude Code - 완료"
    SOUND="Glass"  # macOS 완료음
    ;;
  *)
    URGENCY="low"
    TITLE="Claude Code"
    SOUND="Pop"
    ;;
esac

# OS 감지
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  # terminal-notifier가 있으면 사용 (아이콘 지원)
  if command -v terminal-notifier &> /dev/null; then
    terminal-notifier -title "$TITLE" -message "$MESSAGE" -sound "$SOUND" -appIcon "$CLAWD_ICON" 2>/dev/null
  else
    # osascript 사용 (기본)
    osascript -e "display notification \"$MESSAGE\" with title \"$TITLE\" sound name \"$SOUND\""
  fi
else
  # Linux
  # Clawd 아이콘이 없으면 시스템 아이콘 사용
  if [[ -f "$CLAWD_ICON" ]]; then
    ICON="$CLAWD_ICON"
  else
    ICON="dialog-information"
  fi

  if command -v notify-send &> /dev/null; then
    # DISPLAY 환경변수 설정 (hooks에서 실행 시 필요)
    export DISPLAY="${DISPLAY:-:1}"
    notify-send "$TITLE" "$MESSAGE" -u "$URGENCY" -i "$ICON" -t 2000
  fi
fi

exit 0
