@echo off
cd /d "%~dp0"
start "" http://localhost:3211
node studio/video-server.mjs
pause
