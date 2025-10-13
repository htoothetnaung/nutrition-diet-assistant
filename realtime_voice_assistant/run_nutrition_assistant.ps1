# Nutrition Voice Assistant Launcher
Write-Host "🥗 Starting Nutrition Voice Assistant..." -ForegroundColor Green
Write-Host ""

# Check if Vosk model exists
$voskModelPath = "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15"
if (-not (Test-Path $voskModelPath)) {
    Write-Host "❌ Error: Vosk model not found!" -ForegroundColor Red
    Write-Host "Please download and extract the Vosk model to: $voskModelPath" -ForegroundColor Yellow
    Write-Host "Download from: https://alphacephei.com/vosk/models" -ForegroundColor Cyan
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if nutrition knowledge base exists
$nutritionKbPath = "models\nutrition_kb.json"
if (-not (Test-Path $nutritionKbPath)) {
    Write-Host "⚠️  Warning: Nutrition knowledge base not found!" -ForegroundColor Yellow
    Write-Host "Creating sample dataset and training..." -ForegroundColor Cyan
    Write-Host ""
    
    # Set up and train
    python train_nutrition_assistant.py --setup
    python train_nutrition_assistant.py --dataset data\sample_nutrition_dataset.json
    Write-Host ""
}

# List available audio devices
Write-Host "🎤 Available audio devices:" -ForegroundColor Cyan
python nutrition_app.py --model $voskModelPath --list-devices
Write-Host ""

# Get device index from user
$deviceIndex = Read-Host "Enter microphone device index (or press Enter for default)"
if ([string]::IsNullOrEmpty($deviceIndex)) {
    $deviceIndex = 0
}

Write-Host ""
Write-Host "🚀 Starting Nutrition Voice Assistant with device $deviceIndex..." -ForegroundColor Green
Write-Host "💡 Try asking: 'What are the calories in an apple?'" -ForegroundColor Yellow
Write-Host "📝 Say 'stop listening' to exit." -ForegroundColor Yellow
Write-Host ""

# Run the nutrition assistant
try {
    python nutrition_app.py --model $voskModelPath --nutrition-kb $nutritionKbPath --device $deviceIndex
}
catch {
    Write-Host "❌ Error running the assistant: $_" -ForegroundColor Red
}

Read-Host "Press Enter to exit"
