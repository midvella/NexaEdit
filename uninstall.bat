@echo off
setlocal
cd /d "%~dp0"
if exist ".venv" rmdir /s /q ".venv"
echo NexaEdit kaldirildi. Kaynak dosyalar korunmustur.
pause
