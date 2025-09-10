#!/usr/bin/env python3
"""
Test Multiple Sentences TTS
Test that TTS speaks all sentences consistently.
"""

from utils.tts_pyttsx3 import TTS
import time

def test_multiple_sentences():
    print("=== Multiple Sentences TTS Test ===")
    print("Testing that TTS speaks ALL sentences, not just the first one...")
    print()
    
    # Initialize TTS
    print("Initializing TTS...")
    tts = TTS()
    print()
    
    # Test with multiple sentences
    test_cases = [
        "First sentence should be spoken.",
        "Second sentence should also be spoken.",
        "Third sentence must be spoken too.",
        "Fourth sentence needs to be spoken.",
        "Fifth sentence should definitely be spoken.",
        "Sixth sentence must work as well.",
        "Seventh sentence should be spoken.",
        "Eighth sentence needs to work.",
        "Ninth sentence should be spoken.",
        "Tenth and final sentence must be spoken."
    ]
    
    print(f"Testing {len(test_cases)} sentences...")
    print()
    
    for i, sentence in enumerate(test_cases, 1):
        print(f"Test {i}: {sentence}")
        print("🔊 Speaking...")
        
        try:
            tts.speak(sentence)
            # Wait for TTS to complete
            while tts._is_speaking:
                time.sleep(0.1)
            print("✅ Speech completed successfully")
        except Exception as e:
            print(f"❌ TTS Error: {e}")
        
        print()
        time.sleep(0.5)  # Brief pause between tests
    
    print("All sentence tests completed!")
    print()
    
    # Test rapid fire
    print("Testing rapid fire (no delays)...")
    rapid_sentences = [
        "Rapid one",
        "Rapid two", 
        "Rapid three",
        "Rapid four",
        "Rapid five"
    ]
    
    for sentence in rapid_sentences:
        print(f"Rapid: {sentence}")
        tts.speak(sentence)
        while tts._is_speaking:
            time.sleep(0.1)
        time.sleep(0.1)  # Very short pause
    
    print("Rapid fire test completed!")
    
    # Cleanup
    tts.cleanup()
    print("TTS cleaned up successfully!")

if __name__ == "__main__":
    test_multiple_sentences()

