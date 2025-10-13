#!/usr/bin/env python3
"""
Gemini AI-Powered Nutrition Assistant
Connects to Google Gemini AI and only answers nutrition questions
Blocks all non-nutrition queries
"""

import argparse
import json
import queue
import sys
import time
import os
import re
from typing import Optional, Dict
import google.generativeai as genai

import sounddevice as sd
from utils.stt_vosk import VoskSTT
from utils.tts_pyttsx3 import TTS

class GeminiNutritionAssistant:
    """Gemini AI-powered nutrition assistant that only answers nutrition questions"""
    
    def __init__(self, model_path: str, gemini_api_key: str, nutrition_kb_path: str = "models/accurate_nutrition_kb.json"):
        self.stt = VoskSTT(model_path=model_path, samplerate=16000)
        self.tts = TTS()
        
        # Initialize Gemini AI
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Load nutrition knowledge base
        self.nutrition_data = self.load_nutrition_kb(nutrition_kb_path)
        
        # Nutrition keywords for filtering
        self.nutrition_keywords = [
            "calories", "calorie", "nutrition", "nutrients", "protein", "carbs", "carbohydrates",
            "fat", "fiber", "sugar", "vitamin", "mineral", "healthy", "diet", "food",
            "how many", "how much", "what are", "tell me", "information", "facts",
            "content", "value", "amount", "quantity", "eating", "meal", "breakfast",
            "lunch", "dinner", "snack", "ingredient", "recipe", "cooking", "baking"
        ]
        
        # Diet/workout planning keywords (allowed intent)
        self.plan_keywords = [
            "diet plan", "meal plan", "weekly plan", "7-day plan", "7 day plan",
            "workout", "gym", "exercise", "training", "routine", "program",
            "weight gain", "gain weight", "weight loss", "lose weight", "bulking", "cutting",
            "seven day plan", "7day plan", "seven-day plan"
        ]
        
        # Blocked topics
        self.blocked_topics = [
            "weather", "time", "date", "news", "politics", "sports", "entertainment",
            "technology", "programming", "coding", "games", "movies", "music",
            "travel", "shopping", "money", "finance", "business", "work", "job",
            "school", "education", "science", "history", "geography", "math",
            "personal", "relationship", "family", "friends", "health", "medical",
            "doctor", "hospital", "medicine", "drug", "alcohol", "smoking"
        ]
    
    def load_nutrition_kb(self, kb_path: str) -> list:
        """Load nutrition knowledge base"""
        try:
            if not os.path.exists(kb_path):
                print(f"⚠️  Nutrition knowledge base not found at {kb_path}")
                print("💡 Run 'py simple_accurate_trainer.py' first to create it")
                return []
            
            with open(kb_path, 'r') as f:
                data = json.load(f)
            
            print(f"✅ Loaded nutrition knowledge base with {len(data)} items")
            return data
            
        except Exception as e:
            print(f"❌ Error loading nutrition knowledge base: {e}")
            return []
    
    def is_nutrition_query(self, text: str) -> bool:
        """Check if the query is nutrition-related"""
        text_lower = text.lower()
        
        # Check for nutrition keywords
        has_nutrition_keyword = any(keyword in text_lower for keyword in self.nutrition_keywords)
        
        # Check for blocked topics
        has_blocked_topic = any(topic in text_lower for topic in self.blocked_topics)
        
        # Check for question patterns
        question_patterns = [
            "how many", "how much", "what are", "tell me", "what's in",
            "calories in", "protein in", "carbs in", "fat in", "nutrition",
            "content of", "value of", "amount in", "ingredients in"
        ]
        has_question_pattern = any(pattern in text_lower for pattern in question_patterns)
        
        return has_nutrition_keyword or has_question_pattern
    
    def is_blocked_query(self, text: str) -> bool:
        """Check if the query should be blocked"""
        text_lower = text.lower()
        
        # Allow if it's a plan request
        if self.is_plan_request(text_lower):
            return False
        
        # Check for blocked topics
        has_blocked_topic = any(topic in text_lower for topic in self.blocked_topics)
        
        # Check for non-nutrition questions
        non_nutrition_patterns = [
            "what time", "what date", "what day", "what's the weather",
            "tell me about", "how to", "where is", "when is", "who is",
            "what is", "explain", "define", "meaning of"
        ]
        has_non_nutrition_pattern = any(pattern in text_lower for pattern in non_nutrition_patterns)
        
        return has_blocked_topic or has_non_nutrition_pattern

    def is_plan_request(self, text: str) -> bool:
        """Detect if user asks for a diet/workout plan"""
        t = text.lower()
        # Strong keyword checks
        plan_tokens = ["diet plan", "meal plan", "workout plan", "gym plan", "weekly plan",
                       "7-day plan", "7 day plan", "seven day plan", "seven-day plan",
                       "routine", "program"]
        goals = ["weight gain", "gain weight", "weight loss", "lose weight", "bulking", "cutting"]
        if any(p in t for p in plan_tokens):
            return True
        if ("plan" in t) and ("diet" in t or "meal" in t or "workout" in t or "gym" in t or "training" in t):
            return True
        if any(g in t for g in goals) and ("plan" in t or "diet" in t or "workout" in t or "gym" in t):
            return True
        # Phrases like "weekly diet plan for ..."
        if ("weekly" in t and "plan" in t) and ("diet" in t or "meal" in t or "workout" in t or "gym" in t):
            return True
        return False

    def find_food_in_query(self, text: str) -> Optional[Dict]:
        """Find food item in the query"""
        text_lower = text.lower()
        best_match = None
        best_score = 0
        
        for food in self.nutrition_data:
            score = 0
            
            # Check search terms
            for term in food.get('search_terms', []):
                if term in text_lower:
                    score += 1
            
            # Check direct name match
            if food['name'].lower() in text_lower:
                score += 2
            
            # Check synonyms
            for synonym in food.get('synonyms', []):
                if synonym.lower() in text_lower:
                    score += 1.5
            
            if score > best_score:
                best_score = score
                best_match = {
                    'food_item': food,
                    'confidence': min(score / 3, 1.0)
                }
        
        return best_match if best_score > 0 else None
    
    def get_gemini_response(self, question: str, food_data: Optional[Dict] = None) -> str:
        """Get response from Gemini AI with nutrition context"""
        try:
            # Create system prompt
            system_prompt = '''You are a nutrition expert assistant. You ONLY answer questions about food, nutrition, calories, protein, carbohydrates, fat, vitamins, minerals, and healthy eating. 

You have access to a nutrition database with the following foods and their nutritional information per 100g:
- Calories, Protein, Carbohydrates, Fat, Fiber, Sugar

Rules:
1. ONLY answer nutrition-related questions
2. If asked about non-nutrition topics, politely decline and redirect to nutrition
3. Be helpful and informative about nutrition
4. Use the provided nutrition data when available
5. Keep responses concise and clear
6. Always mention "per 100g" when giving nutritional values

If the user asks about topics other than nutrition, respond with: "I'm a nutrition assistant and can only help with food and nutrition questions. Please ask me about calories, protein, vitamins, or other nutrition topics."'''
            
            # Create user prompt with nutrition data
            user_prompt = question
            
            if food_data:
                food_item = food_data['food_item']
                user_prompt += f"\n\nNutrition data for {food_item['name']} (per 100g):\n"
                user_prompt += f"- Calories: {food_item['calories']}\n"
                user_prompt += f"- Protein: {food_item['protein']}g\n"
                user_prompt += f"- Carbohydrates: {food_item['carbs']}g\n"
                user_prompt += f"- Fat: {food_item['fat']}g\n"
                user_prompt += f"- Fiber: {food_item['fiber']}g\n"
                user_prompt += f"- Sugar: {food_item['sugar']}g\n"
            
            # Call Gemini AI
            full_prompt = f"{system_prompt}\n\nUser Question: {user_prompt}"
            response = self.model.generate_content(full_prompt)
            
            return response.text.strip()
            
        except Exception as e:
            print(f"❌ Gemini AI Error: {e}")
            return "I'm sorry, I'm having trouble connecting to my nutrition database. Please try again later."
    
    def get_plan_response(self, question: str) -> str:
        """Use Gemini to generate a concise 7-day nutrition/workout plan"""
        try:
            system_prompt = '''You are a helpful nutrition and gym planning assistant. Stay within general wellness. Do NOT provide medical advice. If a goal is unclear (e.g., weight gain/loss), assume a safe, general plan.

Rules:
- Provide a concise 7-day plan when asked: include daily meals (breakfast/lunch/dinner/snacks) and a simple workout suggestion (e.g., full-body, push/pull/legs, rest days).
- Portion guidance should be simple (e.g., 1 cup rice, palm-sized protein).
- Emphasize hydration and recovery. Include brief safety notes.
- Keep total response under 220 words.
'''
            user_prompt = f"User request: {question}\nIf relevant, tailor for weight gain/loss with higher/lower calories."
            response = self.model.generate_content(f"{system_prompt}\n\n{user_prompt}")
            return response.text.strip()
        except Exception as e:
            print(f"❌ Gemini AI Error (plan): {e}")
            return "I'm sorry, I couldn't create a plan right now. Please try again."
    
    def generate_reply(self, text: str) -> str:
        """Generate appropriate reply with Gemini AI"""
        t = text.lower().strip()
        
        # Check for stop command
        if "stop listening" in t or t == "stop":
            return "__STOP__"
        
        # Diet/workout plan intent (allowed)
        if self.is_plan_request(t):
            return self.get_plan_response(text)
        
        # Check if it's a blocked query
        if self.is_blocked_query(t):
            return "I'm a nutrition assistant and can only help with food, nutrition, or simple diet/workout planning. Please ask me about calories, protein, vitamins, or a weekly meal/gym plan."
        
        # Check if it's a nutrition query
        if self.is_nutrition_query(t):
            # Find food in the query
            food_data = self.find_food_in_query(text)
            
            # Get response from Gemini AI
            return self.get_gemini_response(text, food_data)
        
        # Handle greetings
        if t in {"hi", "hello", "hey"} or any(x in t for x in ["good morning", "good evening", "good afternoon"]):
            return "Hello! I'm your nutrition assistant powered by Gemini AI. I can help with nutrition facts or create a simple weekly meal/gym plan. What would you like to know?"
        
        if "your name" in t:
            return "I'm your nutrition assistant powered by Gemini AI. I specialize in nutrition info and simple weekly meal/workout plans."
        
        if "help" in t or "what can you do" in t:
            return "I can tell you nutrition facts and create a concise 7-day meal/workout plan. Try: 'meal plan for weight gain' or 'calories in oats'."
        
        # Default response for unclear queries
        return "I'm a nutrition assistant and can help with food nutrition or a simple 7-day meal/workout plan. Please ask about calories, protein, or say 'make me a diet plan'."
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.tts.cleanup()
        except:
            pass

def main():
    parser = argparse.ArgumentParser(description="Gemini AI-Powered Nutrition Voice Assistant")
    parser.add_argument("--model", type=str, required=True, help="Path to Vosk model folder")
    parser.add_argument("--gemini-key", type=str, required=False, default=None, help="Gemini AI API key (or set GEMINI_API_KEY env var)")
    parser.add_argument("--nutrition-kb", type=str, default="models/accurate_nutrition_kb.json",
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
        # Resolve Gemini API key from flag or environment
        gemini_key = args.gemini_key or os.environ.get("GEMINI_API_KEY")
        if not gemini_key:
            print("Error: Gemini API key is required. Pass --gemini-key or set GEMINI_API_KEY environment variable.")
            return
        # Initialize Gemini AI nutrition voice assistant
        print("Initializing Gemini AI-Powered Nutrition Voice Assistant...")
        assistant = GeminiNutritionAssistant(args.model, gemini_key, args.nutrition_kb)
        
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
    
    print("🎤 Gemini AI-Powered Nutrition Assistant ready!")
    print("💡 Say 'RYAN ...' before your question. Example: 'RYAN, how many calories in an apple?' ")
    print("🚫 I ignore all speech without the wake word 'RYAN'")
    print("🛑 Say 'stop listening' anytime to exit.\n")
    
    try:
        with stream:
            last_reminder_ts = 0.0
            while True:
                try:
                    data = q.get()
                    if assistant.stt.accept_waveform(data):
                        result = assistant.stt.get_result()
                        text = result.get("text", "").strip()
                        if not text:
                            continue
                        print(f"📝 You: {text}")
                        
                        lower_text = text.lower()
                        # Global stop command regardless of wake word
                        if "stop listening" in lower_text or lower_text == "stop":
                            assistant.tts.speak("Okay, Have a great day, sir. Bye Bye")
                            break

                        # Mid-speech interrupt: if user says 'stop', halt TTS but keep listening
                        if "stop" in lower_text and assistant.tts.is_speaking():
                            assistant.tts.stop()
                            continue
                        
                        # Strict wake-word gating: process only if 'ryan' present
                        has_ryan = "ryan" in lower_text
                        has_hey_ryan = "hey ryan" in lower_text
                        if not (has_ryan or has_hey_ryan):
                            # Voice reminder if it looks like a question (rate-limited)
                            looks_like_question = any(k in lower_text for k in [
                                "how", "what", "calorie", "calories", "protein", "carb", "fat", "vitamin",
                                "plan", "diet", "workout", "gym", "routine"
                            ]) or lower_text.endswith("?")
                            now_ts = time.time()
                            if looks_like_question and (now_ts - last_reminder_ts) > 3.0:
                                try:
                                    assistant.tts.speak("Please say HEY RYAN or RYAN before your question, then ask.")
                                except Exception:
                                    pass
                                last_reminder_ts = now_ts
                            continue
                        
                        # Extract the part after the first occurrence of wake word
                        try:
                            idx_hey_ryan = lower_text.find("hey ryan")
                            idx_ryan = lower_text.find("ryan")
                            indices = [i for i in [idx_hey_ryan, idx_ryan] if i != -1]
                            wake_index = min(indices) if indices else 0
                            phrase = "hey ryan" if idx_hey_ryan != -1 and (wake_index == idx_hey_ryan) else "ryan"
                            query_raw = text[wake_index + len(phrase):]
                            # Also strip leading wake word artifacts like commas/spaces
                            query_raw = query_raw.lstrip(" ,.:;!?-")
                        except Exception:
                            query_raw = text
                        
                        if not query_raw:
                            try:
                                assistant.tts.speak("Yes? Please ask your question.")
                            except Exception:
                                pass
                            continue
                        
                        reply = assistant.generate_reply(query_raw)
                        if not reply:
                            continue
                        
                        if reply == "__STOP__":
                            assistant.tts.speak("Okay, Have a great day, sir. Bye Bye")
                            break
                        
                        try:
                            print(f"🤖 Nutrition Assistant: {reply}")
                            assistant.tts.speak(reply)
                        except Exception as e:
                            print(f"❌ TTS Error: {e}")
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


