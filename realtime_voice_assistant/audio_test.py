#!/usr/bin/env python3
"""
Audio Device Troubleshooting Script
Run this to diagnose audio device issues before running the main voice assistant.
"""

import sounddevice as sd
import numpy as np
import time
import sys

def test_audio_devices():
    """Test all available audio input devices."""
    print("=== Audio Device Troubleshooting ===\n")
    
    # List all devices
    print("Available audio devices:")
    devices = sd.query_devices()
    input_devices = []
    
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            input_devices.append((i, device))
            print(f"  {i}: {device['name']}")
            print(f"      Channels: {device['max_input_channels']}")
            print(f"      Sample Rate: {device['default_samplerate']} Hz")
            print()
    
    if not input_devices:
        print("❌ No input devices found!")
        print("\nTroubleshooting steps:")
        print("1. Check if a microphone is connected")
        print("2. Check Windows audio settings")
        print("3. Restart Windows Audio service")
        return False
    
    print(f"Found {len(input_devices)} input device(s).\n")
    
    # Test each device
    for device_id, device in input_devices:
        print(f"Testing device {device_id}: {device['name']}")
        try:
            # Test recording for 2 seconds
            duration = 2
            sample_rate = int(device['default_samplerate'])
            
            print(f"  Recording for {duration} seconds at {sample_rate} Hz...")
            recording = sd.rec(int(duration * sample_rate), 
                             samplerate=sample_rate, 
                             channels=1, 
                             device=device_id)
            sd.wait()  # Wait until recording is finished
            
            # Check if we got any audio data
            max_amplitude = np.max(np.abs(recording))
            print(f"  Max amplitude: {max_amplitude:.4f}")
            
            if max_amplitude > 0.001:  # Threshold for detecting audio
                print(f"  ✅ Device {device_id} is working!")
            else:
                print(f"  ⚠️  Device {device_id} may not be picking up audio (low amplitude)")
                
        except Exception as e:
            print(f"  ❌ Error testing device {device_id}: {e}")
        
        print()
    
    return True

def test_sounddevice_installation():
    """Test if sounddevice is properly installed."""
    print("=== SoundDevice Installation Test ===\n")
    
    try:
        print(f"SoundDevice version: {sd.__version__}")
        print(f"PortAudio version: {sd.get_portaudio_version()}")
        print("✅ SoundDevice is properly installed")
        return True
    except Exception as e:
        print(f"❌ SoundDevice installation issue: {e}")
        print("\nTry reinstalling sounddevice:")
        print("  pip install --upgrade sounddevice")
        return False

def main():
    print("Voice Assistant Audio Troubleshooting Tool\n")
    
    # Test installation
    if not test_sounddevice_installation():
        return
    
    print()
    
    # Test devices
    if test_audio_devices():
        print("=== Recommendations ===")
        print("1. Use the device with the highest amplitude for best results")
        print("2. Make sure no other applications are using the microphone")
        print("3. Test with: python app.py --list-devices")
        print("4. Run with: python app.py --model vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15 --device <INDEX>")
    else:
        print("=== No working audio devices found ===")
        print("Please check your microphone connection and Windows audio settings.")

if __name__ == "__main__":
    main()


