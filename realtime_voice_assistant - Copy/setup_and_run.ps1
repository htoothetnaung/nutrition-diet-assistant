# Voice Assistant Setup and Run Script
# This script will help you install Python and run the voice assistant

Write-Host "=== Voice Assistant Setup ===" -ForegroundColor Green
Write-Host ""

# Check if Python is available
$pythonFound = $false
$pythonPath = ""

# Try different Python locations
$pythonPaths = @(
    "python",
    "python3", 
    "py",
    "C:\Program Files\Python313\python.exe",
    "C:\Program Files\Python312\python.exe",
    "C:\Program Files\Python311\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python313\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python312\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311\python.exe"
)

Write-Host "Searching for Python installation..." -ForegroundColor Yellow

foreach ($path in $pythonPaths) {
    try {
        if ($path -eq "python" -or $path -eq "python3" -or $path -eq "py") {
            $result = & $path --version 2>$null
            if ($LASTEXITCODE -eq 0) {
                $pythonFound = $true
                $pythonPath = $path
                Write-Host "Found Python: $path" -ForegroundColor Green
                break
            }
        } else {
            if (Test-Path $path) {
                $result = & $path --version 2>$null
                if ($LASTEXITCODE -eq 0) {
                    $pythonFound = $true
                    $pythonPath = $path
                    Write-Host "Found Python: $path" -ForegroundColor Green
                    break
                }
            }
        }
    } catch {
        # Continue searching
    }
}

if (-not $pythonFound) {
    Write-Host "Python not found. Let's install it!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Choose installation method:" -ForegroundColor Yellow
    Write-Host "1. Download from python.org (Recommended)"
    Write-Host "2. Install via Microsoft Store"
    Write-Host "3. Install via winget (if available)"
    Write-Host ""
    
    $choice = Read-Host "Enter your choice (1-3)"
    
    switch ($choice) {
        "1" {
            Write-Host "Opening Python download page..." -ForegroundColor Yellow
            Start-Process "https://www.python.org/downloads/"
            Write-Host "Please download and install Python, then run this script again."
            Read-Host "Press Enter to continue"
            exit
        }
        "2" {
            Write-Host "Installing Python from Microsoft Store..." -ForegroundColor Yellow
            Start-Process "ms-windows-store://pdp/?ProductId=9NRWMJP3717K"
            Write-Host "Please install Python from the Microsoft Store, then run this script again."
            Read-Host "Press Enter to continue"
            exit
        }
        "3" {
            try {
                Write-Host "Installing Python via winget..." -ForegroundColor Yellow
                winget install Python.Python.3.12
                Write-Host "Python installed! Please restart your terminal and run this script again."
                Read-Host "Press Enter to continue"
                exit
            } catch {
                Write-Host "Winget not available. Please use option 1 or 2." -ForegroundColor Red
                Read-Host "Press Enter to continue"
                exit
            }
        }
        default {
            Write-Host "Invalid choice. Please run the script again." -ForegroundColor Red
            exit
        }
    }
}

Write-Host ""
Write-Host "Python found: $pythonPath" -ForegroundColor Green
Write-Host ""

# Check if required packages are installed
Write-Host "Checking required packages..." -ForegroundColor Yellow

$packages = @("sounddevice", "pyttsx3", "vosk", "numpy")
$missingPackages = @()

foreach ($package in $packages) {
    try {
        $result = & $pythonPath -c "import $package" 2>$null
        if ($LASTEXITCODE -ne 0) {
            $missingPackages += $package
        } else {
            Write-Host "✓ $package" -ForegroundColor Green
        }
    } catch {
        $missingPackages += $package
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host ""
    Write-Host "Installing missing packages: $($missingPackages -join ', ')" -ForegroundColor Yellow
    & $pythonPath -m pip install $missingPackages
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install packages. Please run: pip install $($missingPackages -join ' ')" -ForegroundColor Red
        Read-Host "Press Enter to continue"
        exit
    }
}

Write-Host ""
Write-Host "All packages installed!" -ForegroundColor Green
Write-Host ""

# Check if Vosk model exists
if (-not (Test-Path "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15")) {
    Write-Host "Vosk model not found!" -ForegroundColor Red
    Write-Host "Please download the model from: https://alphacephei.com/vosk/models" -ForegroundColor Yellow
    Write-Host "Extract it to: vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15" -ForegroundColor Yellow
    Read-Host "Press Enter to continue"
    exit
}

Write-Host "Vosk model found!" -ForegroundColor Green
Write-Host ""

# Run the voice assistant
Write-Host "Starting Voice Assistant..." -ForegroundColor Green
Write-Host ""

# First, list devices
Write-Host "Available audio devices:" -ForegroundColor Yellow
& $pythonPath app.py --list-devices

Write-Host ""
$deviceChoice = Read-Host "Enter device index (or press Enter for auto-detect)"

if ($deviceChoice -eq "") {
    & $pythonPath app.py --model "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15"
} else {
    & $pythonPath app.py --model "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15" --device $deviceChoice
}

Write-Host ""
Write-Host "Voice Assistant stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"

