#!/usr/bin/env bash
# PostToolUse hook (Write|Edit): ruff-format only the edited Python file (the old
# hook ran `ruff format` on the whole repo after every edit).
set -u
f="$(jq -r '.tool_input.file_path // .tool_response.filePath // empty' 2>/dev/null)"
case "$f" in *.py) ;; *) exit 0 ;; esac
[ -f "$f" ] || exit 0
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
case "$f" in "$REPO"/*) ;; *) exit 0 ;; esac
"$REPO/.venv/bin/ruff" format --quiet "$f"
