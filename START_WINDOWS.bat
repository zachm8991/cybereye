@echo off
cd /d "%~dp0"
py -3 -m venv .venv
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto fail
.venv\Scripts\python.exe main.py
pause
exit /b
:fail
echo Setup failed. Install Python 3.10 or newer from python.org with the Python launcher.
pause
