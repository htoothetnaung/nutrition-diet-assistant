# Voice Assistant Troubleshooting Guide

## Common Sound Device Issues and Solutions

### 1. Python Not Found
**Error**: `Python was not found; run without arguments to install from the Microsoft Store`

**Solutions**:
- Install Python from [python.org](https://python.org) (recommended)
- Or install from Microsoft Store
- Make sure Python is added to your PATH environment variable

### 2. SoundDevice Installation Issues
**Error**: `Import "sounddevice" could not be resolved`

**Solutions**:
```bash
pip install sounddevice
# or
pip install --upgrade sounddevice
```

### 3. No Audio Devices Found
**Error**: `No input devices found` or `PortAudioError`

**Solutions**:
1. **Check microphone connection**:
   - Ensure microphone is properly connected
   - Try unplugging and reconnecting
   - Test microphone in Windows Sound settings

2. **Check Windows Audio Service**:
   - Press `Win + R`, type `services.msc`
   - Find "Windows Audio" service
   - Right-click → Start (if stopped)
   - Set startup type to "Automatic"

3. **Check microphone permissions**:
   - Go to Windows Settings → Privacy → Microphone
   - Ensure "Allow apps to access your microphone" is ON
   - Allow access for your Python application

4. **Update audio drivers**:
   - Go to Device Manager
   - Find "Audio inputs and outputs"
   - Right-click your microphone → Update driver

### 4. Device Access Denied
**Error**: `[Errno -9996] Invalid input device` or `[Errno -9998] Invalid device`

**Solutions**:
1. **Close other audio applications**:
   - Close Skype, Discord, Zoom, etc.
   - Close any recording software

2. **Try different device index**:
   ```bash
   python app.py --list-devices
   python app.py --model vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15 --device 1
   ```

3. **Run as Administrator** (if needed)

### 5. Low Audio Quality or No Speech Recognition
**Issues**: Assistant doesn't respond to voice commands

**Solutions**:
1. **Check microphone levels**:
   - Right-click speaker icon → Open Sound settings
   - Click "Device properties" under Input
   - Adjust microphone level to 70-80%

2. **Test with audio test script**:
   ```bash
   python audio_test.py
   ```

3. **Use a different sample rate**:
   ```bash
   python app.py --model vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15 --device 1 --samplerate 44100
   ```

### 6. TTS (Text-to-Speech) Issues
**Error**: `pyttsx3` not working or no sound output

**Solutions**:
1. **Install TTS dependencies**:
   ```bash
   pip install pyttsx3
   ```

2. **Check Windows TTS settings**:
   - Go to Control Panel → Speech Recognition
   - Test text-to-speech functionality

3. **Try different TTS engines** (modify `utils/tts_pyttsx3.py`):
   ```python
   # Add this to test different voices
   voices = self.engine.getProperty("voices")
   for voice in voices:
       print(voice.id)
   ```

## Quick Diagnostic Steps

1. **Run the audio test**:
   ```bash
   python audio_test.py
   ```

2. **List available devices**:
   ```bash
   python app.py --list-devices
   ```

3. **Test with specific device**:
   ```bash
   python app.py --model vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15 --device 0
   ```

4. **Use the batch file** (Windows):
   ```bash
   run_voice_assistant.bat
   ```

## Windows-Specific Issues

### Windows Audio Service
If you get audio device errors, restart the Windows Audio service:
1. Press `Win + R`, type `services.msc`
2. Find "Windows Audio" and "Windows Audio Endpoint Builder"
3. Right-click each → Restart

### Microphone Privacy Settings
1. Go to Settings → Privacy & Security → Microphone
2. Turn ON "Microphone access"
3. Turn ON "Let apps access your microphone"

### Real-time Protection
Sometimes Windows Defender blocks audio access:
1. Go to Windows Security → Virus & threat protection
2. Add exclusion for your Python installation folder

## Still Having Issues?

1. **Check the logs**: Look for specific error messages in the console output
2. **Try different devices**: Use `--list-devices` to see all available options
3. **Test with other applications**: Try recording with Windows Voice Recorder
4. **Restart your computer**: Sometimes audio drivers need a fresh start

## Contact Information

If you continue to have issues, please provide:
- Your operating system version
- Python version (`python --version`)
- Complete error message
- Output from `python audio_test.py`


