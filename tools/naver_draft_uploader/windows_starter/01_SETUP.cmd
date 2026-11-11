@echo off
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
set "PY=py"
set "PYARGS=-3"
py -3 -c "import sys;sys.exit(0 if sys.version_info >= (3,11) else 1)" >nul 2>nul
if not errorlevel 1 goto have_python
set "PY=python"
set "PYARGS="
python -c "import sys;sys.exit(0 if sys.version_info >= (3,11) else 1)" >nul 2>nul
if not errorlevel 1 goto have_python
echo Python 3.11 or newer is required. Install Python from python.org first.
echo No administrator or paid browser account is required by this package.
pause
exit /b 2
:have_python
if exist ".venv\Scripts\python.exe" goto install_packages
%PY% %PYARGS% -m venv ".venv"
if errorlevel 1 goto failed
:install_packages
".venv\Scripts\python.exe" -m pip install --index-url https://pypi.org/simple -r requirements.txt
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -I starter.py diagnose
if errorlevel 1 goto diagnose_incomplete
echo SETUP COMPLETE. Next: 02_LOGIN.cmd
pause
exit /b 0
:diagnose_incomplete
echo Installation finished, but local diagnostics need attention.
echo Open reports\diagnose.json. No article was uploaded.
pause
exit /b 2
:failed
echo SETUP FAILED. No browser login or upload was attempted.
pause
exit /b 3
