@echo off
cd /d "%~dp0"
start "" http://localhost:3211
node app/server.mjs
pause
