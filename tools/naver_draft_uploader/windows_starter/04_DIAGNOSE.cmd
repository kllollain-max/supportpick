@echo off
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
if not exist ".venv\Scripts\python.exe" goto missing
".venv\Scripts\python.exe" -I starter.py diagnose
set "RC=%ERRORLEVEL%"
pause
exit /b %RC%
:missing
echo Run 01_SETUP.cmd first.
pause
exit /b 2
