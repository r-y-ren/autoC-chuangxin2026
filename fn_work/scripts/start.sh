#!/usr/bin/env bash
# 验收入口（R13）：scripts/start.sh --selfcheck → ../start.sh
exec bash "$(dirname "$0")/../start.sh" "$@"
