#!/bin/bash
# Pre-write hook: check for common issues before file writes

FILE_PATH="${TOOL_INPUT_FILE_PATH:-}"

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Block writes to sensitive files
case "$FILE_PATH" in
  *.env|*.env.*|*/.secret/*)
    echo "BLOCKED: Cannot write to sensitive file: $FILE_PATH"
    exit 1
    ;;
esac

exit 0
