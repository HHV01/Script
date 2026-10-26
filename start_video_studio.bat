@echo off
cd /d "%~dp0"
start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'http://localhost:3211'"
node app/server.mjs
pause
