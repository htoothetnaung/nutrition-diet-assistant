@echo off
echo Highly Accurate Nutrition Voice Assistant
echo =========================================
echo.

REM Check if Vosk model exists
if not exist "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15" (
    echo Error: Vosk model not found!
    echo Please download and extract the Vosk model to: vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15
    echo Download from: https://alphacephei.com/vosk/models
    pause
    exit /b 1
)

REM Check if accurate nutrition knowledge base exists
if not exist "models\accurate_nutrition_kb.json" (
    echo Error: Accurate nutrition knowledge base not found!
    echo Please run the training script first:
    echo   py simple_accurate_trainer.py
    pause
    exit /b 1
)

REM List available audio devices
echo Available audio devices:
py highly_accurate_app.py --model "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15" --list-devices
echo.

REM Get device index from user
set /p device_index="Enter microphone device index (or press Enter for default): "
if "%device_index%"=="" set device_index=0

echo.
echo Starting Highly Accurate Nutrition Assistant with device %device_index%...
echo Say 'stop listening' to exit.
echo.

REM Run the highly accurate nutrition assistant
py highly_accurate_app.py --model "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15" --nutrition-kb "models\accurate_nutrition_kb.json" --device %device_index%

pause








