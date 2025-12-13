# 🎙️ Voice Assistant Integration Guide

## Overview

The voice assistant has been successfully integrated into your Streamlit nutrition app! This guide will help you understand how to use and configure the voice features.

## 🚀 Quick Start

### 1. Run the App

```bash
streamlit run app.py
```

### 2. Access Voice Assistant

1. Log in to the app
2. Navigate to the "🎙️ Voice Assistant" tab
3. Click "🎤 Start Voice Assistant"
4. Wait for the confirmation message
5. Say "RYAN" followed by your nutrition question

## 🎯 Voice Commands

### Basic Commands

- **"RYAN, how many calories in an apple?"**
- **"RYAN, what's a good post-workout meal?"**
- **"RYAN, create a 7-day meal plan"**
- **"RYAN, how much protein do I need?"**
- **"RYAN, stop listening"** (to end the session)

### Supported Topics

- 🥗 **Nutrition Facts**: Calories, protein, carbs, fat, vitamins, minerals
- 🏃 **Fitness & Exercise**: Workout plans, pre/post-workout nutrition
- 🍽️ **Meal Planning**: 7-day meal plans, recipe suggestions
- 💪 **Health & Wellness**: Hydration, sleep, general health tips

## ⚙️ Configuration

### API Keys

The voice assistant uses AssemblyAI for natural language processing. The API key is already configured:

- **AssemblyAI API Key**: `32a11032d56d438497638cd2b8e6fd5a`

### Voice Settings

- **Language**: English (US) - default
- **Speech Speed**: Adjustable from 0.5x to 2.0x
- **Voice Type**: Natural, Friendly, Professional, or Calm

## 🔧 Technical Details

### Dependencies Installed

- `vosk==0.3.45` - Speech-to-text recognition
- `sounddevice==0.4.7` - Audio input/output
- `pyttsx3==2.99` - Text-to-speech synthesis
- `assemblyai>=0.33.0` - Natural language processing

### File Structure

```
nutrition-diet-assistant/
├── assembly_nutrition_assistant.py    # Main voice assistant module
├── utils/
│   ├── __init__.py
│   ├── stt_vosk.py                   # Speech-to-text utilities
│   └── tts_pyttsx3.py                # Text-to-speech utilities
├── vosk-model-small-en-us-0.15/      # Vosk speech recognition model
├── models/
│   └── accurate_nutrition_kb.json    # Nutrition knowledge base
└── app.py                            # Main Streamlit app with voice tab
```

## 🎤 How It Works

1. **Wake Word Detection**: The system listens for "RYAN" to activate
2. **Speech Recognition**: Vosk converts your speech to text
3. **Natural Language Processing**: AssemblyAI LeMUR processes your question
4. **Knowledge Base Lookup**: Searches the nutrition database for relevant information
5. **Response Generation**: Creates a personalized nutrition response
6. **Text-to-Speech**: Converts the response back to speech

## 🛠️ Troubleshooting

### Common Issues

#### Voice Assistant Won't Start

- **Check microphone permissions**: Ensure your browser/system allows microphone access
- **Verify dependencies**: Run `python test_voice_integration.py` to check installation
- **Check audio devices**: Make sure your microphone is working

#### No Response to "RYAN"

- **Speak clearly**: Pronounce "RYAN" distinctly
- **Check microphone**: Ensure your microphone is not muted
- **Try again**: Sometimes the wake word needs to be said more clearly

#### AssemblyAI Errors

- **Check internet connection**: AssemblyAI requires internet access
- **Verify API key**: The key should be automatically set
- **Check rate limits**: AssemblyAI has usage limits

### Testing the Integration

Run the test script to verify everything is working:

```bash
python test_voice_integration.py
```

Expected output:

```
🧪 Testing Voice Assistant Integration
==================================================
✅ All tests passed! Voice assistant integration is ready.
```

## 🎯 Usage Tips

1. **Speak Clearly**: Enunciate your words for better recognition
2. **Use the Wake Word**: Always start with "RYAN" before your question
3. **Be Specific**: Ask specific nutrition questions for better responses
4. **Test Voice First**: Use the "🔊 Test Voice" button to verify audio output
5. **Stop When Done**: Say "stop listening" to end the session

## 🔄 Integration with Main App

The voice assistant is fully integrated with your existing nutrition app:

- **User Authentication**: Only works when logged in
- **Session Management**: Voice interactions are part of your user session
- **Data Persistence**: Voice conversations can be saved to chat history
- **Consistent UI**: Matches the design and functionality of other tabs

## 🚀 Next Steps

1. **Test the Integration**: Try the voice assistant with different nutrition questions
2. **Customize Settings**: Adjust voice speed and language preferences
3. **Save Conversations**: Use the "📋 Save Conversation" button to store important interactions
4. **Explore Features**: Try asking about meal plans, nutrition facts, and health tips

## 📞 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Run the test script to verify installation
3. Check the browser console for any error messages
4. Ensure all dependencies are properly installed

---

**Happy voice-assisted nutrition tracking! 🎙️🥗**
