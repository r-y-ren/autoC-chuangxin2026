@echo off
rem 双击即开操控台（Windows）
cd /d %~dp0
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe scripts\launch.py %*
) else (
  py -3 scripts\launch.py %* || python scripts\launch.py %*
)
