#!/usr/bin/env bash
# 双击/执行即开操控台（自动起服务+开浏览器）
set -u
cd "$(dirname "$0")"
PY=.venv/bin/python
[ -x "$PY" ] || PY=python3
exec "$PY" scripts/launch.py "$@"
