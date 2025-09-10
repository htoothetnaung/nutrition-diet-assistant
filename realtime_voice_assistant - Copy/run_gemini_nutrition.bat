@echo off
echo Gemini AI-Powered Nutrition Assistant
echo =====================================
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
if not exist "models\accurate_nutrition_kb.json" (
    echo Error: Nutrition knowledge base not found!
    echo Please run the training script first:
    echo   py simple_accurate_trainer.py
    pause
    exit /b 1
)

REM Resolve Gemini API key from environment or prompt
set "gemini_key=%GEMINI_API_KEY%"
if "%gemini_key%"=="" (
    set /p gemini_key="Enter your Gemini AI API key (or set GEMINI_API_KEY env var): "
    if "%gemini_key%"=="" (
        echo Error: Gemini AI API key is required!
        echo Get your API key from: https://makersuite.google.com/app/apikey
        pause
        exit /b 1
    )
)

REM List available audio devices
echo Available audio devices:
py gemini_nutrition_assistant.py --model "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15" --gemini-key "%gemini_key%" --list-devices
echo.

REM Get device index from user
set /p device_index="Enter microphone device index (or press Enter for default): "
if "%device_index%"=="" set device_index=0

echo.
echo Starting Gemini AI-Powered Nutrition Assistant with device %device_index%...
echo I will only answer nutrition questions and block other topics.
echo Say 'stop listening' to exit.
echo.

REM Run the Gemini AI nutrition assistant
py gemini_nutrition_assistant.py --model "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15" --gemini-key "%gemini_key%" --nutrition-kb "models\accurate_nutrition_kb.json" --device %device_index%

pause


