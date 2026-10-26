@echo off
setlocal
cd /d "%~dp0vieneu"
set "UV_PROJECT_ENVIRONMENT=%LOCALAPPDATA%\VideoStudio\vieneu-venv"
set "PYTHONIOENCODING=utf-8"
set "HF_HUB_DISABLE_SYMLINKS_WARNING=1"
if not exist "%UV_PROJECT_ENVIRONMENT%\Scripts\python.exe" (
  echo Chua co VieNeu-TTS, dang cai dat lan dau...
  uv sync --extra cuda
  if errorlevel 1 (
    echo Cai dat that bai. Kiem tra Python/uv/GPU.
    pause
    exit /b 1
  )
)
echo VieNeu-TTS: http://127.0.0.1:8000
uv run python -m apps.openai_speech
pause
