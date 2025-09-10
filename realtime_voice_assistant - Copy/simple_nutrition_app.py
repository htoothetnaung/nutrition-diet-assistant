#!/usr/bin/env python3
"""
Simplified Nutrition Voice Assistant (without torch dependencies)
"""

import argparse
import json
import queue
import sys
import time
import os
import re
from typing import Optional

import sounddevice as sd
from utils.stt_vosk import VoskSTT
from utils.tts_pyttsx3 import TTS

class SimpleNutritionAssistant:
    """Simplified nutrition voice assistant"""
    
    def __init__(self, model_path: str, nutrition_kb_path: str = "models/nutrition_kb.json"):
        self.stt = VoskSTT(model_path=model_path, samplerate=16000)
        self.tts = TTS()
        
        # Load nutrition knowledge base
        self.nutrition_data = self.load_nutrition_kb(nutrition_kb_path)
        
        # Nutrition-related keywords
        self.nutrition_keywords = [
            "calories", "calorie", "nutrition", "nutrients", "protein", "carbs", "carbohydrates",
            "fat", "fiber", "sugar", "vitamin", "mineral", "healthy", "diet", "food"
        ]
        
        self.food_queries = [
            "what's in", "what is in", "nutritional value", "calories in", "protein in",
            "carbs in", "fat in", "how many calories", "nutrition facts"
        ]
    
    def load_nutrition_kb(self, kb_path: str) -> list:
        """Load nutrition knowledge base"""
        try:
            if os.path.exists(kb_path):
                with open(kb_path, 'r') as f:
                    data = json.load(f)
                print(f"✅ Loaded nutrition knowledge base with {len(data)} items")
                return data
            else:
                print(f"⚠️  Nutrition knowledge base not found at {kb_path}")
                return []
        except Exception as e:
            print(f"❌ Error loading nutrition knowledge base: {e}")
            return []
    
    def is_nutrition_query(self, text: str) -> bool:
        """Check if the query is nutrition-related"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.nutrition_keywords)
    
    def extract_food_name(self, text: str) -> Optional[str]:
        """Extract food name from nutrition query"""
        text_lower = text.lower()
        
        # Remove common query patterns
        for pattern in self.food_queries:
            text_lower = text_lower.replace(pattern, "").strip()
        
        # Remove common words
        common_words = ["the", "a", "an", "in", "of", "for", "with", "and", "or"]
        words = [word for word in text_lower.split() if word not in common_words]
        
        if words:
            return " ".join(words)
        return None
    
    def find_food(self, query: str) -> Optional[dict]:
        """Find food item using simple text matching"""
        query_lower = query.lower()
        
        # Direct name match
        for item in self.nutrition_data:
            if query_lower in item['name'].lower():
                return item
        
        # Synonym match
        for item in self.nutrition_data:
            for synonym in item.get('synonyms', []):
                if query_lower in synonym.lower():
                    return item
        
        # Partial match
        for item in self.nutrition_data:
            if any(word in item['name'].lower() for word in query_lower.split()):
                return item
        
        return None
    
    def generate_nutrition_reply(self, text: str) -> str:
        """Generate nutrition-specific reply"""
        if not self.nutrition_data:
            return "I don't have nutrition information available. Please load a nutrition dataset first."
        
        food_name = self.extract_food_name(text)
        if not food_name:
            return "I didn't catch the food name. Please try asking about a specific food item."
        
        # Search for the food
        food_item = self.find_food(food_name)
        
        if not food_item:
            return f"I don't have nutrition information for '{food_name}'. Try asking about a different food."
        
        # Generate nutrition response
        response = f"Here's the nutrition information for {food_item['name']}:\n"
        response += f"• Calories: {food_item['calories']} per 100g\n"
        response += f"• Protein: {food_item['protein']}g\n"
        response += f"• Carbohydrates: {food_item['carbs']}g\n"
        response += f"• Fat: {food_item['fat']}g\n"
        
        if food_item.get('fiber', 0) > 0:
            response += f"• Fiber: {food_item['fiber']}g\n"
        if food_item.get('sugar', 0) > 0:
            response += f"• Sugar: {food_item['sugar']}g\n"
        
        if food_item.get('description'):
            response += f"\n{food_item['description']}"
        
        return response
    
    def generate_reply(self, text: str) -> str:
        """Generate appropriate reply based on query type"""
        t = text.lower().strip()
        
        # Check for stop command
        if "stop listening" in t or t == "stop":
            return "__STOP__"
        
        # Check if it's a nutrition query
        if self.is_nutrition_query(t):
            return self.generate_nutrition_reply(text)
        
        # Handle general queries
        if t in {"hi", "hello", "hey"} or any(x in t for x in ["good morning", "good evening", "good afternoon"]):
            return "Hello! I'm your nutrition voice assistant. Ask me about food nutrition facts!"
        
        if "your name" in t:
            return "I'm your nutrition voice assistant. I can help you with food nutrition information!"
        
        if "time" in t:
            return time.strftime("It's %I:%M %p.")
        
        if "date" in t or "day" in t:
            return time.strftime("Today is %A, %B %d, %Y.")
        
        if "help" in t or "what can you do" in t:
            return "I can help you with nutrition information! Try asking things like 'What are the calories in an apple?' or 'Tell me about chicken nutrition'."
        
        if t:
            return f"You said: {text}. I'm a nutrition assistant - try asking me about food nutrition facts!"
        return ""
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.tts.cleanup()
        except:
            pass

def main():
    parser = argparse.ArgumentParser(description="Simple Nutrition Voice Assistant")
    parser.add_argument("--model", type=str, required=True, help="Path to Vosk model folder")
    parser.add_argument("--nutrition-kb", type=str, default="models/nutrition_kb.json",
                       help="Path to nutrition knowledge base")
    parser.add_argument("--samplerate", type=int, default=16000, help="Microphone sample rate")
    parser.add_argument("--device", type=int, default=None, help="sounddevice input device index")
    parser.add_argument("--list-devices", action="store_true", help="List available audio devices and exit")
    args = parser.parse_args()
    
    # List devices and exit if requested
    if args.list_devices:
        print("Available audio devices:")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"  {i}: {device['name']} (Input: {device['max_input_channels']} channels)")
        return
    
    try:
        # Initialize nutrition voice assistant
        print("Initializing Simple Nutrition Voice Assistant...")
        assistant = SimpleNutritionAssistant(args.model, args.nutrition_kb)
        
        # Print audio devices if device not specified
        if args.device is None:
            print("\nAvailable input devices:")
            devices = sd.query_devices()
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    print(f"  {i}: {device['name']} (Input: {device['max_input_channels']} channels)")
            print("\nUse --device INDEX to select a microphone.")
            print("Use --list-devices to see all devices and exit.")
            return
        
        # Test device availability
        try:
            test_devices = sd.query_devices(args.device)
            if test_devices['max_input_channels'] == 0:
                print(f"Error: Device {args.device} does not support input.")
                return
        except Exception as e:
            print(f"Error: Invalid device index {args.device}. {e}")
            return
        
        q = queue.Queue()
        
        def audio_callback(indata, frames, time_info, status):
            if status:
                print(f"Audio status: {status}", file=sys.stderr)
            q.put(bytes(indata))
        
        print(f"Setting up audio stream with device {args.device}...")
        stream = sd.RawInputStream(
            samplerate=args.samplerate,
            blocksize=8000,  # ~0.5s
            device=args.device,
            dtype="int16",
            channels=1,
            callback=audio_callback
        )
        
    except Exception as e:
        print(f"Error initializing audio components: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you have a microphone connected")
        print("2. Check if another application is using the microphone")
        print("3. Try running with --list-devices to see available devices")
        print("4. On Windows, make sure Windows Audio service is running")
        return
    
    print("🎤 Simple Nutrition Assistant ready! Ask me about food nutrition facts!")
    print("💡 Try: 'What are the calories in an apple?' or 'Tell me about chicken nutrition'")
    print("📝 Say 'stop listening' to exit.\n")
    
    try:
        with stream:
            while True:
                try:
                    data = q.get()
                    if assistant.stt.accept_waveform(data):
                        result = assistant.stt.get_result()
                        text = result.get("text", "").strip()
                        if not text:
                            continue
                        print(f"📝 You: {text}")
                        
                        reply = assistant.generate_reply(text)
                        if not reply:
                            continue
                        
                        if reply == "__STOP__":
                            assistant.tts.speak("Okay, I will stop listening now. Goodbye!")
                            break
                        
                        # Avoid feedback: pause mic while speaking
                        stream.stop()
                        try:
                            print(f"🤖 Nutrition Assistant: {reply}")
                            assistant.tts.speak(reply)
                        except Exception as e:
                            print(f"❌ TTS Error: {e}")
                        finally:
                            stream.start()
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Error processing audio: {e}")
                    continue
    except sd.PortAudioError as e:
        print(f"Audio device error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure the microphone is not being used by another application")
        print("2. Try a different device index with --device")
        print("3. Restart the application")
        print("4. Check Windows audio settings")
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Please check your audio setup and try again.")
    finally:
        # Clean up
        try:
            assistant.cleanup()
        except:
            pass

if __name__ == "__main__":
    main()








