#!/bin/bash
# Convenience wrapper: loads your saved Yuanbao cookie, then runs wx_audio.py.
# Save your cookie once (see README "Getting the cookie"):
#   mkdir -p ~/.config/wechat-audio
#   echo 'hy_user=...; hy_token=...' > ~/.config/wechat-audio/cookie
#   chmod 600 ~/.config/wechat-audio/cookie
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COOKIE_FILE="$HOME/.config/wechat-audio/cookie"
if [ -f "$COOKIE_FILE" ]; then
  export YUANBAO_COOKIE="$(cat "$COOKIE_FILE")"
fi
exec python3 "$SCRIPT_DIR/wx_audio.py" "$@"
