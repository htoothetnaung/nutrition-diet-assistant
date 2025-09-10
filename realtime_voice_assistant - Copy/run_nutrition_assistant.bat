@echo off
echo Starting Nutrition Voice Assistant...
echo.

REM Check if Vosk model exists
if not exist "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15" (
    echo Error: Vosk model not found!
    echo Please download and extract the Vosk model to: vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15
    echo Download from: https://alphacephei.com/vosk/models
    pause
    exit /b 1
)

REM Check if nutrition knowledge base exists
if not exist "models\nutrition_kb.json" (
    echo Warning: Nutrition knowledge base not found!
    echo Creating sample dataset and training...
    echo.
    python train_nutrition_assistant.py --setup
    python train_nutrition_assistant.py --dataset data\sample_nutrition_dataset.json
    echo.
)

REM List available audio devices
echo Available audio devices:
python nutrition_app.py --model "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15" --list-devices
echo.

REM Get device index from user
set /p device_index="Enter microphone device index (or press Enter for default): "
if "%device_index%"=="" set device_index=0

echo.
echo Starting Nutrition Voice Assistant with device %device_index%...
echo Say 'stop listening' to exit.
echo.

REM Run the nutrition assistant
python nutrition_app.py --model "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15" --nutrition-kb "models\nutrition_kb.json" --device %device_index%

pause
