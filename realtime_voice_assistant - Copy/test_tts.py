#!/usr/bin/env python3
"""
TTS Test Script
Test the Text-to-Speech functionality to ensure it works properly.
"""

from utils.tts_pyttsx3 import TTS
import time

def test_tts():
    print("=== TTS Test ===")
    print("Testing Text-to-Speech functionality...")
    print()
    
    # Initialize TTS
    print("Initializing TTS...")
    tts = TTS()
    print()
    
    # Test messages
    test_messages = [
        "Hello! This is the first test message.",
        "This is the second test message.",
        "This is the third test message.",
        "Testing multiple calls to ensure TTS works consistently.",
        "Final test message. TTS should work properly now."
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}: {message}")
        print("🔊 Speaking...")
        
        try:
            tts.speak(message)
            print("✅ Speech completed successfully")
        except Exception as e:
            print(f"❌ TTS Error: {e}")
        
        print()
        time.sleep(1)  # Brief pause between tests
    
    print("TTS test completed!")
    print()
    
    # Test rapid successive calls
    print("Testing rapid successive calls...")
    rapid_messages = [
        "Quick test one",
        "Quick test two", 
        "Quick test three"
    ]
    
    for message in rapid_messages:
        print(f"Rapid test: {message}")
        tts.speak(message)
        time.sleep(0.5)
    
    print("Rapid test completed!")
    
    # Cleanup
    tts.cleanup()
    print("TTS cleaned up successfully!")

if __name__ == "__main__":
    test_tts()

