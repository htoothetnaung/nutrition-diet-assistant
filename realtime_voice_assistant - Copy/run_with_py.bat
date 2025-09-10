@echo off
echo Voice Assistant - Python Launcher
echo ==================================

REM Try different Python commands
echo Trying to find Python...

REM Try 'py' launcher (most reliable on Windows)
py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Found Python via 'py' launcher
    goto :run_app
)

REM Try 'python3'
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Found Python3
    set PYTHON_CMD=python3
    goto :run_app
)

REM Try 'python'
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Found Python
    set PYTHON_CMD=python
    goto :run_app
)

REM Try full path to Python 3.13
if exist "C:\Program Files\Python313\python.exe" (
    echo Found Python 3.13
    set PYTHON_CMD="C:\Program Files\Python313\python.exe"
    goto :run_app
)

REM Try other common Python paths
if exist "C:\Program Files\Python312\python.exe" (
    echo Found Python 3.12
    set PYTHON_CMD="C:\Program Files\Python312\python.exe"
    goto :run_app
)

if exist "C:\Program Files\Python311\python.exe" (
    echo Found Python 3.11
    set PYTHON_CMD="C:\Program Files\Python311\python.exe"
    goto :run_app
)

REM Try user AppData paths
if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python313\python.exe" (
    echo Found Python 3.13 in AppData
    set PYTHON_CMD="%USERPROFILE%\AppData\Local\Programs\Python\Python313\python.exe"
    goto :run_app
)

if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe" (
    echo Found Python 3.12 in AppData
    set PYTHON_CMD="%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe"
    goto :run_app
)

echo Python not found!
echo.
echo Please install Python from one of these sources:
echo 1. https://www.python.org/downloads/ (Recommended)
echo 2. Microsoft Store
echo 3. Use winget: winget install Python.Python.3.12
echo.
echo After installing Python, run this script again.
pause
exit /b 1

:run_app
echo.
echo Python found! Starting Voice Assistant...
echo.

REM Check if model exists
if not exist "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15" (
    echo Vosk model not found!
    echo Please download from: https://alphacephei.com/vosk/models
    echo Extract to: vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15
    pause
    exit /b 1
)

REM Install required packages if needed
echo Checking dependencies...
%PYTHON_CMD% -m pip install sounddevice pyttsx3 vosk numpy --quiet

REM Run the application
echo.
echo Choose an option:
echo 1. List audio devices
echo 2. Test audio devices  
echo 3. Run voice assistant (auto-detect device)
echo 4. Run voice assistant (select device)
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    %PYTHON_CMD% app.py --list-devices
) else if "%choice%"=="2" (
    %PYTHON_CMD% audio_test.py
) else if "%choice%"=="3" (
    %PYTHON_CMD% app.py --model "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15"
) else if "%choice%"=="4" (
    %PYTHON_CMD% app.py --list-devices
    echo.
    set /p device="Enter device index: "
    %PYTHON_CMD% app.py --model "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15" --device %device%
) else (
    echo Invalid choice.
)

echo.
pause

