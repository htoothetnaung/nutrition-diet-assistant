@echo off
echo Voice Assistant Launcher
echo ========================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Please install Python or add it to your PATH.
    pause
    exit /b 1
)

REM Check if model directory exists
if not exist "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15" (
    echo Vosk model not found. Please download and extract the model.
    echo Download from: https://alphacephei.com/vosk/models
    pause
    exit /b 1
)

echo.
echo Choose an option:
echo 1. List audio devices
echo 2. Test audio devices
echo 3. Run voice assistant (auto-detect device)
echo 4. Run voice assistant (select device)
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    python app.py --list-devices
) else if "%choice%"=="2" (
    python audio_test.py
) else if "%choice%"=="3" (
    python app.py --model "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15"
) else if "%choice%"=="4" (
    python app.py --list-devices
    echo.
    set /p device="Enter device index: "
    python app.py --model "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15" --device %device%
) else (
    echo Invalid choice.
)

pause


