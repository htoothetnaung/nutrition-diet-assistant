#!/bin/bash
echo "Gemini AI-Powered Nutrition Assistant"
echo "====================================="
echo ""

# Check if Vosk model exists
if [ ! -d "vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15" ]; then
    echo "Error: Vosk model not found!"
    echo "Please download and extract the Vosk model to: vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15"
    echo "Download from: https://alphacephei.com/vosk/models"
    read -p "Press Enter to exit"
    exit 1
fi

# Check if nutrition knowledge base exists
if [ ! -f "models/accurate_nutrition_kb.json" ]; then
    echo "Error: Nutrition knowledge base not found!"
    echo "Please run the training script first:"
    echo "  py simple_accurate_trainer.py"
    read -p "Press Enter to exit"
    exit 1
fi

# Get Gemini AI API key
echo -n "Enter your Gemini AI API key: "
read gemini_key
if [ -z "$gemini_key" ]; then
    echo "Error: Gemini AI API key is required!"
    echo "Get your API key from: https://makersuite.google.com/app/apikey"
    read -p "Press Enter to exit"
    exit 1
fi

# List available audio devices
echo "Available audio devices:"
py gemini_nutrition_assistant.py --model "vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15" --gemini-key "test" --list-devices
echo ""

# Get device index from user
echo -n "Enter microphone device index (or press Enter for default): "
read device_index
if [ -z "$device_index" ]; then
    device_index=0
fi

echo ""
echo "Starting Gemini AI-Powered Nutrition Assistant with device $device_index..."
echo "I will only answer nutrition questions and block other topics."
echo "Say 'stop listening' to exit."
echo ""

# Run the Gemini AI nutrition assistant
py gemini_nutrition_assistant.py --model "vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15" --gemini-key "$gemini_key" --nutrition-kb "models/accurate_nutrition_kb.json" --device $device_index

read -p "Press Enter to exit"







