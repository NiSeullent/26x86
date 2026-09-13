@echo off
REM 26x86 — Windows entry (wizard-first)
cd /d "%~dp0"
python -m x86 wizard %*
