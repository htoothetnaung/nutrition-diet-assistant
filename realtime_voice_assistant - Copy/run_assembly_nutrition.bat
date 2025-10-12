@echo off
setlocal

REM Ensure Python is available
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher not found. Please install Python 3 and ensure 'py' is in PATH.
  exit /b 1
)

echo Installing dependencies (this may take a minute)...
py -m pip install -r requirements.txt --quiet

set /p AAI_KEY=Enter your AssemblyAI API key: 
if "%AAI_KEY%"=="" (
  echo AssemblyAI API key is required.
  exit /b 1
)

echo.
echo Listing input devices...
py app.py --list-devices --model "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15"
echo.
set /p DEV_INDEX=Enter microphone device index (press Enter to use 0): 
if "%DEV_INDEX%"=="" set DEV_INDEX=0

set MODEL=vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15
if not exist "%MODEL%" (
  echo Vosk model not found at %MODEL%
  echo Please download and place the model at the expected path.
  exit /b 1
)

set ASSEMBLYAI_API_KEY=%AAI_KEY%
echo Starting AssemblyAI Nutrition Assistant...
py assembly_nutrition_assistant.py --model "%MODEL%" --device %DEV_INDEX%

endlocal

