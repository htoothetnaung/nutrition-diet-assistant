#!/bin/bash
echo "OpenAI-Powered Nutrition Assistant"
echo "=================================="
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

# Get OpenAI API key
echo -n "Enter your OpenAI API key: "
read openai_key
if [ -z "$openai_key" ]; then
    echo "Error: OpenAI API key is required!"
    echo "Get your API key from: https://platform.openai.com/api-keys"
    read -p "Press Enter to exit"
    exit 1
fi

# List available audio devices
echo "Available audio devices:"
py openai_nutrition_assistant.py --model "vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15" --openai-key "test" --list-devices
echo ""

# Get device index from user
echo -n "Enter microphone device index (or press Enter for default): "
read device_index
if [ -z "$device_index" ]; then
    device_index=0
fi

echo ""
echo "Starting OpenAI-Powered Nutrition Assistant with device $device_index..."
echo "I will only answer nutrition questions and block other topics."
echo "Say 'stop listening' to exit."
echo ""

# Run the OpenAI nutrition assistant
py openai_nutrition_assistant.py --model "vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15" --openai-key "$openai_key" --nutrition-kb "models/accurate_nutrition_kb.json" --device $device_index

read -p "Press Enter to exit"







