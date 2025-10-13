#!/usr/bin/env python3
"""
Highly Accurate Nutrition Voice Assistant
Uses the improved training for maximum accuracy
"""

import argparse
import json
import queue
import sys
import time
import os
import re
from typing import Optional, Dict

import sounddevice as sd
from utils.stt_vosk import VoskSTT
from utils.tts_pyttsx3 import TTS

class HighlyAccurateNutritionAssistant:
    """Highly accurate nutrition voice assistant with improved training"""
    
    def __init__(self, model_path: str, nutrition_kb_path: str = "models/accurate_nutrition_kb.json"):
        self.stt = VoskSTT(model_path=model_path, samplerate=16000)
        self.tts = TTS()
        
        # Load improved nutrition knowledge base
        self.nutrition_data = self.load_accurate_kb(nutrition_kb_path)
        
        # Enhanced nutrition keywords
        self.nutrition_keywords = [
            "calories", "calorie", "nutrition", "nutrients", "protein", "carbs", "carbohydrates",
            "fat", "fiber", "sugar", "vitamin", "mineral", "healthy", "diet", "food",
            "how many", "how much", "what are", "tell me", "information", "facts",
            "content", "value", "amount", "quantity"
        ]
    
    def load_accurate_kb(self, kb_path: str) -> list:
        """Load accurate nutrition knowledge base"""
        try:
            if not os.path.exists(kb_path):
                print(f"❌ Accurate knowledge base not found at {kb_path}")
                print("💡 Run 'py simple_accurate_trainer.py' first to create it")
                return []
            
            with open(kb_path, 'r') as f:
                data = json.load(f)
            
            print(f"✅ Loaded highly accurate nutrition knowledge base with {len(data)} items")
            return data
            
        except Exception as e:
            print(f"❌ Error loading accurate knowledge base: {e}")
            return []
    
    def is_nutrition_query(self, text: str) -> bool:
        """Enhanced nutrition query detection"""
        text_lower = text.lower()
        
        # Check for nutrition keywords
        has_nutrition_keyword = any(keyword in text_lower for keyword in self.nutrition_keywords)
        
        # Check for question patterns
        question_patterns = [
            "how many", "how much", "what are", "tell me", "what's in",
            "calories in", "protein in", "carbs in", "fat in", "nutrition",
            "content of", "value of", "amount in"
        ]
        has_question_pattern = any(pattern in text_lower for pattern in question_patterns)
        
        return has_nutrition_keyword or has_question_pattern
    
    def find_best_food_match(self, question: str) -> Optional[Dict]:
        """Find best food match using comprehensive search"""
        question_lower = question.lower()
        best_match = None
        best_score = 0
        
        for food in self.nutrition_data:
            score = 0
            
            # Check search terms (most important)
            for term in food.get('search_terms', []):
                if term in question_lower:
                    score += 1
            
            # Check direct name match (high priority)
            if food['name'].lower() in question_lower:
                score += 2
            
            # Check synonyms (medium priority)
            for synonym in food.get('synonyms', []):
                if synonym.lower() in question_lower:
                    score += 1.5
            
            # Check category (low priority)
            if food.get('category', '').lower() in question_lower:
                score += 0.5
            
            if score > best_score:
                best_score = score
                best_match = {
                    'food_item': food,
                    'confidence': min(score / 3, 1.0),  # Normalize to 0-1
                    'matched_method': 'comprehensive_search'
                }
        
        return best_match if best_score > 0 else None
    
    def generate_nutrition_reply(self, text: str) -> str:
        """Generate highly accurate nutrition reply"""
        if not self.nutrition_data:
            return "I don't have nutrition information available. Please load a nutrition dataset first."
        
        # Find best match
        match_result = self.find_best_food_match(text)
        
        if not match_result:
            return f"I couldn't find nutrition information for that food. Try asking about specific foods like apple, banana, chicken breast, or eggs."
        
        food_item = match_result['food_item']
        confidence = match_result['confidence']
        
        # Generate response based on question type
        question_lower = text.lower()
        
        if "calories" in question_lower or "calorie" in question_lower:
            response = f"{food_item['name']} has {food_item['calories']} calories per 100g."
        elif "protein" in question_lower:
            response = f"{food_item['name']} contains {food_item['protein']}g of protein per 100g."
        elif "carbs" in question_lower or "carbohydrates" in question_lower:
            response = f"{food_item['name']} has {food_item['carbs']}g of carbohydrates per 100g."
        elif "fat" in question_lower:
            response = f"{food_item['name']} contains {food_item['fat']}g of fat per 100g."
        elif "fiber" in question_lower:
            response = f"{food_item['name']} has {food_item['fiber']}g of fiber per 100g."
        elif "sugar" in question_lower:
            response = f"{food_item['name']} contains {food_item['sugar']}g of sugar per 100g."
        else:
            # Full nutrition information
            response = f"Here's the complete nutrition information for {food_item['name']}:\n"
            response += f"• Calories: {food_item['calories']} per 100g\n"
            response += f"• Protein: {food_item['protein']}g\n"
            response += f"• Carbohydrates: {food_item['carbs']}g\n"
            response += f"• Fat: {food_item['fat']}g\n"
            
            if food_item.get('fiber', 0) > 0:
                response += f"• Fiber: {food_item['fiber']}g\n"
            if food_item.get('sugar', 0) > 0:
                response += f"• Sugar: {food_item['sugar']}g\n"
        
        # Add confidence indicator for debugging (only if low confidence)
        if confidence < 0.7:
            response += f"\n(Note: I'm {confidence*100:.0f}% confident about this match)"
        
        return response
    
    def generate_reply(self, text: str) -> str:
        """Generate appropriate reply with maximum accuracy"""
        t = text.lower().strip()
        
        # Check for stop command
        if "stop listening" in t or t == "stop":
            return "__STOP__"
        
        # Check if it's a nutrition query
        if self.is_nutrition_query(t):
            return self.generate_nutrition_reply(text)
        
        # Handle general queries
        if t in {"hi", "hello", "hey"} or any(x in t for x in ["good morning", "good evening", "good afternoon"]):
            return "Hello! I'm your highly accurate nutrition voice assistant. Ask me about food nutrition facts!"
        
        if "your name" in t:
            return "I'm your highly accurate nutrition voice assistant. I can help you with detailed food nutrition information!"
        
        if "time" in t:
            return time.strftime("It's %I:%M %p.")
        
        if "date" in t or "day" in t:
            return time.strftime("Today is %A, %B %d, %Y.")
        
        if "help" in t or "what can you do" in t:
            return "I can help you with detailed nutrition information! Try asking things like 'How many calories in an apple?' or 'What's the protein content of chicken breast?'"
        
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
    parser = argparse.ArgumentParser(description="Highly Accurate Nutrition Voice Assistant")
    parser.add_argument("--model", type=str, required=True, help="Path to Vosk model folder")
    parser.add_argument("--nutrition-kb", type=str, default="models/accurate_nutrition_kb.json",
                       help="Path to accurate nutrition knowledge base")
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
        # Initialize highly accurate nutrition voice assistant
        print("Initializing Highly Accurate Nutrition Voice Assistant...")
        assistant = HighlyAccurateNutritionAssistant(args.model, args.nutrition_kb)
        
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
    
    print("🎤 Highly Accurate Nutrition Assistant ready!")
    print("💡 Try: 'How many calories in an apple?' or 'What's the protein content of chicken breast?'")
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
                            print(f"🤖 Accurate Assistant: {reply}")
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








