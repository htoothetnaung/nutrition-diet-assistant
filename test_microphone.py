#!/usr/bin/env python3
"""
Test microphone functionality
"""

import sounddevice as sd
import numpy as np
import time


def test_microphone():
    """Test if microphone is working"""
    print("🎤 Testing microphone...")

    # List available devices
    print("\n📱 Available audio devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device["max_input_channels"] > 0:  # Input device
            print(
                f"  Device {i}: {device['name']} (Input channels: {device['max_input_channels']})"
            )

    # Test recording from default device
    print("\n🔊 Testing recording from default device...")
    try:
        duration = 3  # seconds
        sample_rate = 16000

        print(f"Recording for {duration} seconds... Speak now!")
        recording = sd.rec(
            int(duration * sample_rate), samplerate=sample_rate, channels=1
        )
        sd.wait()  # Wait until recording is finished

        # Check if we got any audio
        max_amplitude = np.max(np.abs(recording))
        print(f"Max amplitude: {max_amplitude:.4f}")

        if max_amplitude > 0.01:
            print("✅ Microphone is working! Audio detected.")
            return True
        else:
            print(
                "❌ No audio detected. Check microphone permissions or try a different device."
            )
            return False

    except Exception as e:
        print(f"❌ Error testing microphone: {e}")
        return False


def test_specific_device(device_index):
    """Test a specific device"""
    print(f"\n🎤 Testing device {device_index}...")
    try:
        duration = 3
        sample_rate = 16000

        print(f"Recording for {duration} seconds... Speak now!")
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            device=device_index,
        )
        sd.wait()

        max_amplitude = np.max(np.abs(recording))
        print(f"Max amplitude: {max_amplitude:.4f}")

        if max_amplitude > 0.01:
            print(f"✅ Device {device_index} is working!")
            return True
        else:
            print(f"❌ Device {device_index} - No audio detected.")
            return False

    except Exception as e:
        print(f"❌ Error testing device {device_index}: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Microphone Test")
    print("=" * 50)

    # Test default device
    if not test_microphone():
        print("\n🔄 Trying other devices...")
        # Test other devices
        for device_index in [0, 2, 3, 4]:
            if test_specific_device(device_index):
                print(f"\n✅ Use device {device_index} for voice assistant!")
                break
        else:
            print(
                "\n❌ No working microphone found. Check permissions and device connections."
            )
