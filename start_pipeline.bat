@echo off
cd /d "%~dp0"
echo Kiem tra VieNeu-TTS...
powershell -NoProfile -Command "try{(Invoke-WebRequest http://127.0.0.1:8000/health -UseBasicParsing -TimeoutSec 1)|Out-Null;exit 0}catch{exit 1}"
if errorlevel 1 start "VieNeu-TTS" cmd /c "tools\start-vieneu.bat"
echo Kiem tra Video Studio...
powershell -NoProfile -Command "try{(Invoke-WebRequest http://127.0.0.1:3211/api/state -UseBasicParsing -TimeoutSec 1)|Out-Null;exit 0}catch{exit 1}"
if errorlevel 1 start "Video Studio" cmd /c "node app/server.mjs"
timeout /t 3 >nul
start "" http://localhost:3211/pipeline.html
