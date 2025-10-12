@echo off
echo CSV Nutrition Data Checker
echo ========================
echo.

if "%1"=="" (
    echo Usage: check_csv.bat your_file.csv
    echo Example: check_csv.bat my_nutrition_data.csv
    echo.
    pause
    exit /b 1
)

echo Checking your CSV file: %1
echo.

REM Try different Python commands
python prepare_csv.py %1 2>nul
if %errorlevel% equ 0 goto :success

py prepare_csv.py %1 2>nul
if %errorlevel% equ 0 goto :success

python3 prepare_csv.py %1 2>nul
if %errorlevel% equ 0 goto :success

echo.
echo Python not found in PATH. Please try one of these:
echo 1. Install Python from python.org
echo 2. Use the full path to Python
echo 3. Run: py -3 prepare_csv.py %1
echo.
pause
exit /b 1

:success
echo.
echo CSV check completed!
echo.
pause



