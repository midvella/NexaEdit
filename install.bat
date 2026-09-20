@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul || (echo Python Launcher bulunamadi. Python 3.14 x64 kurun.& exit /b 1)
if exist ".venv\Scripts\python.exe" .venv\Scripts\python.exe -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3,14) else 1)"
if errorlevel 1 rmdir /s /q .venv
if not exist ".venv\Scripts\python.exe" py -3.14 -m venv .venv
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto fail
echo NexaEdit kuruldu.
pause
exit /b 0
:fail
echo Kurulum basarisiz. Python 3.14 x64 ve Tcl/Tk kurulu olmali.
pause
exit /b 1
