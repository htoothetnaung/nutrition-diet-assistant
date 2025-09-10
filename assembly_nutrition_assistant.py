#!/usr/bin/env python3
"""
AssemblyAI-Powered Nutrition Assistant
Replaces Gemini with AssemblyAI LeMUR for Q&A/plan generation while retaining Vosk STT and pyttsx3 TTS.
"""

import argparse
import json
import os
import queue
import sys
import time
from datetime import datetime
from typing import Optional, Dict

import sounddevice as sd

# Add the utils directory to the path
utils_path = os.path.join(os.path.dirname(__file__), "utils")
if utils_path not in sys.path:
    sys.path.insert(0, utils_path)

from stt_vosk import VoskSTT
from tts_pyttsx3 import TTS

try:
    import assemblyai as aai
except Exception:
    aai = None


class AssemblyNutritionAssistant:
    def __init__(
        self,
        model_path: str,
        assembly_key: str,
        nutrition_kb_path: str = "models/accurate_nutrition_kb.json",
        device_index: int = 0,
        log_callback=None,
    ):
        self.stt = VoskSTT(model_path=model_path, samplerate=16000)
        self.tts = TTS(rate=200)
        self.device_index = device_index
        self.log_callback = log_callback

        if not assembly_key:
            raise ValueError("AssemblyAI API key is required")
        if aai is None:
            raise ImportError(
                "assemblyai package not installed. Run: py -m pip install assemblyai"
            )

        aai.settings.api_key = assembly_key

        self.nutrition_data = self.load_nutrition_kb(nutrition_kb_path)

        # Allowed intents keywords
        self.nutrition_keywords = [
            "calories",
            "calorie",
            "nutrition",
            "nutrients",
            "protein",
            "carbs",
            "carbohydrates",
            "fat",
            "fiber",
            "sugar",
            "vitamin",
            "mineral",
            "healthy",
            "diet",
            "food",
            "how many",
            "how much",
            "what are",
            "tell me",
            "information",
            "facts",
            "content",
            "value",
            "amount",
            "quantity",
            "eating",
            "meal",
            "breakfast",
            "lunch",
            "dinner",
            "snack",
            "ingredient",
            "recipe",
            "cooking",
            "baking",
        ]

        self.gym_keywords = [
            "gym",
            "workout",
            "exercise",
            "training",
            "routine",
            "program",
            "strength",
            "cardio",
            "running",
            "walking",
            "push",
            "pull",
            "legs",
            "rest day",
            "warm up",
            "cool down",
            "stretch",
            "mobility",
            "reps",
            "sets",
        ]

        self.health_keywords = [
            "health",
            "wellness",
            "hydration",
            "sleep",
            "steps",
            "heart rate",
            "bmi",
            "balanced diet",
            "portion",
            "lifestyle",
            "recovery",
        ]

        self.plan_keywords = [
            "diet plan",
            "meal plan",
            "weekly plan",
            "7-day plan",
            "7 day plan",
            "workout",
            "gym",
            "exercise",
            "training",
            "routine",
            "program",
            "weight gain",
            "gain weight",
            "weight loss",
            "lose weight",
            "bulking",
            "cutting",
            "seven day plan",
            "7day plan",
            "seven-day plan",
        ]

        # Non-supported topics (we still avoid medical advice)
        self.blocked_topics = [
            "weather",
            "time",
            "date",
            "news",
            "politics",
            "sports",
            "entertainment",
            "technology",
            "programming",
            "coding",
            "games",
            "movies",
            "music",
            "travel",
            "shopping",
            "money",
            "finance",
            "business",
            "work",
            "job",
            "school",
            "education",
            "science",
            "history",
            "geography",
            "math",
            "personal",
            "relationship",
            "family",
            "friends",
            "medical",
            "doctor",
            "hospital",
            "medicine",
            "drug",
            "alcohol",
            "smoking",
        ]

    def log(self, message, log_type="system"):
        """Log a message to both console and UI"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"

        # Print to console
        print(formatted_message)

        # Send to UI callback if available
        if self.log_callback:
            self.log_callback(message, log_type)

    def load_nutrition_kb(self, kb_path: str) -> list:
        try:
            if not os.path.exists(kb_path):
                print(f"⚠️  Nutrition knowledge base not found at {kb_path}")
                print("💡 Run 'py simple_accurate_trainer.py' first to create it")
                return []
            with open(kb_path, "r") as f:
                data = json.load(f)
            print(f"✅ Loaded nutrition knowledge base with {len(data)} items")
            return data
        except Exception as e:
            print(f"❌ Error loading nutrition knowledge base: {e}")
            return []

    def is_plan_request(self, text: str) -> bool:
        t = text.lower()
        plan_tokens = [
            "diet plan",
            "meal plan",
            "workout plan",
            "gym plan",
            "weekly plan",
            "7-day plan",
            "7 day plan",
            "seven day plan",
            "seven-day plan",
            "routine",
            "program",
        ]
        goals = [
            "weight gain",
            "gain weight",
            "weight loss",
            "lose weight",
            "bulking",
            "cutting",
        ]
        if any(p in t for p in plan_tokens):
            return True
        if ("plan" in t) and (
            "diet" in t
            or "meal" in t
            or "workout" in t
            or "gym" in t
            or "training" in t
        ):
            return True
        if any(g in t for g in goals) and (
            "plan" in t or "diet" in t or "workout" in t or "gym" in t
        ):
            return True
        if ("weekly" in t and "plan" in t) and (
            "diet" in t or "meal" in t or "workout" in t or "gym" in t
        ):
            return True
        return False

    def is_nutrition_query(self, text: str) -> bool:
        text_lower = text.lower()
        has_nutrition_keyword = any(
            keyword in text_lower for keyword in self.nutrition_keywords
        )
        has_gym_keyword = any(keyword in text_lower for keyword in self.gym_keywords)
        has_health_keyword = any(
            keyword in text_lower for keyword in self.health_keywords
        )
        question_patterns = [
            "how many",
            "how much",
            "what are",
            "tell me",
            "what's in",
            "calories in",
            "protein in",
            "carbs in",
            "fat in",
            "nutrition",
            "content of",
            "value of",
            "amount in",
            "ingredients in",
        ]
        has_question_pattern = any(
            pattern in text_lower for pattern in question_patterns
        )
        return (
            has_nutrition_keyword
            or has_gym_keyword
            or has_health_keyword
            or has_question_pattern
        )

    def is_blocked_query(self, text: str) -> bool:
        text_lower = text.lower()
        if self.is_plan_request(text_lower):
            return False
        has_blocked_topic = any(topic in text_lower for topic in self.blocked_topics)
        non_nutrition_patterns = [
            "what time",
            "what date",
            "what day",
            "what's the weather",
            "tell me about",
            "how to",
            "where is",
            "when is",
            "who is",
            "what is",
            "explain",
            "define",
            "meaning of",
        ]
        has_non_nutrition_pattern = any(
            pattern in text_lower for pattern in non_nutrition_patterns
        )
        return has_blocked_topic or has_non_nutrition_pattern

    def find_food_in_query(self, text: str) -> Optional[Dict]:
        text_lower = text.lower()
        best_match = None
        best_score = 0
        for food in self.nutrition_data:
            score = 0
            for term in food.get("search_terms", []):
                if term in text_lower:
                    score += 1
            if food["name"].lower() in text_lower:
                score += 2
            for synonym in food.get("synonyms", []):
                if synonym.lower() in text_lower:
                    score += 1.5
            if score > best_score:
                best_score = score
                best_match = {"food_item": food, "confidence": min(score / 3, 1.0)}
        return best_match if best_score > 0 else None

    def generate_kb_answer(
        self, question: str, food_data: Optional[Dict]
    ) -> Optional[str]:
        """Fast path: answer directly from local KB when possible (no API call)."""
        if not food_data:
            return None
        q = question.lower()
        item = food_data["food_item"]
        # Map nutrient keywords to KB keys and units
        nutrient_map = {
            "calorie": ("calories", ""),
            "calories": ("calories", ""),
            "protein": ("protein", "g"),
            "carb": ("carbs", "g"),
            "carbs": ("carbs", "g"),
            "fat": ("fat", "g"),
            "fiber": ("fiber", "g"),
            "sugar": ("sugar", "g"),
        }
        # Detect which nutrient is asked for (or all)
        selected = None
        for key in nutrient_map.keys():
            if key in q:
                selected = key
                break
        if selected is None and any(
            k in q for k in ["nutrition", "nutrients", "macros", "values"]
        ):
            # Return compact macro summary
            return (
                f"Per 100g, {item['name']} has: "
                f"{item['calories']} calories, {item['protein']}g protein, {item['carbs']}g carbs, {item['fat']}g fat."
            )
        if selected is None:
            # If user asked "how many" and food identified, default to calories
            if "how many" in q or "how much" in q:
                selected = "calories"
        if selected:
            kb_key, unit = nutrient_map[selected]
            value = item.get(kb_key)
            if value is not None:
                unit_str = f" {unit}" if unit else ""
                return f"According to the nutrition data provided, 100g of {item['name']} contains {value}{unit_str} {kb_key}."
        return None

    def lemur_ask(self, question: str, food_data: Optional[Dict] = None) -> str:
        """Use LeMUR to generate a response. We pass the nutrition rules as system prompt."""
        prompt = (
            "You are a helpful wellness assistant. You can answer questions about: \n"
            "- Food and nutrition (calories, protein, carbs, fat, vitamins, minerals)\n"
            "- General health and wellness (hydration, sleep, steps, recovery) — NO medical advice\n"
            "- Gym and fitness (simple workouts, sets/reps, warmups, rest days)\n\n"
            "Rules:\n"
            "1. Stay within nutrition, general wellness, and simple gym/fitness guidance\n"
            "2. Do NOT provide medical advice or diagnose conditions\n"
            "3. Be concise and practical; use any provided nutrition data when relevant\n"
            "4. When giving nutrition values, mention 'per 100g' if data is per 100g\n"
            "5. If asked about unrelated topics, politely redirect to nutrition/health/gym scope\n"
        )

        user_prompt = question
        if food_data:
            food_item = food_data["food_item"]
            user_prompt += (
                f"\n\nNutrition data for {food_item['name']} (per 100g):\n"
                f"- Calories: {food_item['calories']}\n"
                f"- Protein: {food_item['protein']}g\n"
                f"- Carbohydrates: {food_item['carbs']}g\n"
                f"- Fat: {food_item['fat']}g\n"
                f"- Fiber: {food_item['fiber']}g\n"
                f"- Sugar: {food_item['sugar']}g\n"
            )

        try:
            # LeMUR uses aai.Lemur for text tasks; content can be provided as input_text
            task = aai.Lemur().task(
                input_text=user_prompt,
                prompt=prompt,
                final_model="anthropic/claude-3-haiku",
            )
            return (
                task.response or ""
            ).strip() or "I'm sorry, I couldn't generate a response."
        except Exception as e:
            print(f"❌ AssemblyAI LeMUR Error: {e}")
            return "I'm sorry, I'm having trouble connecting to my nutrition service. Please try again later."

    def lemur_plan(self, question: str) -> str:
        try:
            prompt = (
                "You are a helpful nutrition and gym planning assistant. Stay within general wellness. "
                "Do NOT provide medical advice. If a goal is unclear (e.g., weight gain/loss), assume a safe, general plan.\n\n"
                "Rules:\n"
                "- Provide a concise 7-day plan when asked: include daily meals (breakfast/lunch/dinner/snacks) and a simple workout suggestion.\n"
                "- Portion guidance should be simple (e.g., 1 cup rice, palm-sized protein).\n"
                "- Emphasize hydration and recovery. Include brief safety notes.\n"
                "- Keep total response under 220 words."
            )
            task = aai.Lemur().task(
                input_text=question,
                prompt=prompt,
                final_model="anthropic/claude-3-haiku",
            )
            return (
                task.response or ""
            ).strip() or "I could not create a plan right now."
        except Exception as e:
            print(f"❌ AssemblyAI LeMUR Error (plan): {e}")
            return "I'm sorry, I couldn't create a plan right now. Please try again."

    def generate_reply(self, text: str) -> str:
        t = text.lower().strip()
        if "stop listening" in t or t == "stop":
            return "__STOP__"
        if self.is_plan_request(t):
            return self.lemur_plan(text)
        if self.is_blocked_query(t):
            return (
                "I'm a nutrition assistant and can only help with food, nutrition, or simple diet/workout planning. "
                "Please ask me about calories, protein, vitamins, or a weekly meal/gym plan."
            )
        if self.is_nutrition_query(t):
            food_data = self.find_food_in_query(text)
            # Try fast KB answer first
            kb_answer = self.generate_kb_answer(text, food_data)
            if kb_answer:
                return kb_answer
            # Fallback to LLM
            return self.lemur_ask(text, food_data)
        if t in {"hi", "hello", "hey"} or any(
            x in t for x in ["good morning", "good evening", "good afternoon"]
        ):
            return "Hello! I can help with nutrition facts, general health tips, and simple gym plans. What would you like to know?"
        if "your name" in t:
            return "I'm your nutrition assistant. I specialize in nutrition info and simple weekly meal/workout plans."
        if "help" in t or "what can you do" in t:
            return "I can provide nutrition facts, general health tips (sleep, hydration, steps), and simple gym guidance, plus 7-day meal/workout plans."
        return (
            "I can help with nutrition info, general health tips, and simple gym guidance, or create a 7-day meal/workout plan. "
            "Try: 'Ryan, calories in oats' or 'Ryan, a 3-day beginner workout'."
        )

    def start_listening(self):
        """Start listening for voice input in a separate thread"""
        import threading
        import queue

        self.audio_queue = queue.Queue()
        self.is_listening = True

        def audio_callback(indata, frames, time_info, status):
            if status:
                print(f"Audio status: {status}", file=sys.stderr)
            if self.is_listening:
                self.audio_queue.put(bytes(indata))

        try:
            self.stream = sd.RawInputStream(
                samplerate=16000,
                blocksize=3000,
                device=self.device_index,
                dtype="int16",
                channels=1,
                latency="low",
                callback=audio_callback,
            )

            def listen_loop():
                with self.stream:
                    while self.is_listening:
                        try:
                            data = self.audio_queue.get(timeout=0.1)
                            if self.stt.accept_waveform(data):
                                result = self.stt.get_result()
                                text = result.get("text", "").strip()
                                if not text:
                                    continue

                                lower_text = text.lower()

                                # Check for stop commands
                                if (
                                    "stop listening" in lower_text
                                    or lower_text == "stop"
                                ):
                                    self.tts.speak("Okay, Have a great day. Bye bye.")
                                    self.is_listening = False
                                    break

                                # Check for wake word
                                has_ryan = ("hey ryan" in lower_text) or (
                                    "ryan" in lower_text
                                )
                                if not has_ryan:
                                    continue

                                try:
                                    idx_hey_ryan = lower_text.find("hey ryan")
                                    idx_ryan = lower_text.find("ryan")
                                    indices = [
                                        i for i in [idx_hey_ryan, idx_ryan] if i != -1
                                    ]
                                    wake_index = min(indices) if indices else 0
                                    phrase = (
                                        "hey ryan"
                                        if idx_hey_ryan != -1
                                        and (wake_index == idx_hey_ryan)
                                        else "ryan"
                                    )
                                    query_raw = text[wake_index + len(phrase) :]
                                    query_raw = query_raw.lstrip(" ,.:;!?-")
                                except Exception:
                                    query_raw = text

                                if not query_raw:
                                    self.tts.speak("Yes? Please ask your question.")
                                    continue

                                self.log(query_raw, "user")
                                reply = self.generate_reply(query_raw)
                                if not reply:
                                    continue
                                if reply == "__STOP__":
                                    self.log("Okay, Have a great day. Bye bye.", "tts")
                                    self.tts.speak("Okay, Have a great day. Bye bye.")
                                    self.is_listening = False
                                    break

                                try:
                                    self.log(reply, "assistant")
                                    self.log(reply, "tts")
                                    self.tts.speak(reply)
                                    self.log("✅ Speech completed", "system")
                                except Exception as e:
                                    error_msg = f"TTS Error: {e}"
                                    self.log(error_msg, "error")

                        except queue.Empty:
                            continue
                        except Exception as e:
                            print(f"Error processing audio: {e}")
                            continue

            self.listen_thread = threading.Thread(target=listen_loop, daemon=True)
            self.listen_thread.start()
            return True

        except Exception as e:
            print(f"Error starting audio stream: {e}")
            return False

    def stop_listening(self):
        """Stop listening for voice input"""
        self.is_listening = False
        if hasattr(self, "stream"):
            try:
                self.stream.stop()
            except:
                pass

    def cleanup(self):
        try:
            self.stop_listening()
            self.tts.cleanup()
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(
        description="AssemblyAI-Powered Nutrition Voice Assistant"
    )
    parser.add_argument(
        "--model", type=str, required=True, help="Path to Vosk model folder"
    )
    parser.add_argument(
        "--assembly-key",
        type=str,
        required=False,
        default=None,
        help="AssemblyAI API key (or set ASSEMBLYAI_API_KEY env var)",
    )
    parser.add_argument(
        "--nutrition-kb",
        type=str,
        default="models/accurate_nutrition_kb.json",
        help="Path to nutrition knowledge base",
    )
    parser.add_argument(
        "--samplerate", type=int, default=16000, help="Microphone sample rate"
    )
    parser.add_argument(
        "--device", type=int, default=None, help="sounddevice input device index"
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List available audio devices and exit",
    )
    args = parser.parse_args()

    if args.list_devices:
        print("Available audio devices:")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device["max_input_channels"] > 0:
                print(
                    f"  {i}: {device['name']} (Input: {device['max_input_channels']} channels)"
                )
        return

    try:
        assembly_key = args.assembly_key or os.environ.get("ASSEMBLYAI_API_KEY")
        if not assembly_key:
            print(
                "Error: AssemblyAI API key is required. Pass --assembly-key or set ASSEMBLYAI_API_KEY environment variable."
            )
            return

        print("Initializing AssemblyAI-Powered Nutrition Voice Assistant...")
        assistant = AssemblyNutritionAssistant(
            args.model, assembly_key, args.nutrition_kb
        )

        if args.device is None:
            print("\nAvailable input devices:")
            devices = sd.query_devices()
            for i, device in enumerate(devices):
                if device["max_input_channels"] > 0:
                    print(
                        f"  {i}: {device['name']} (Input: {device['max_input_channels']} channels)"
                    )
            print("\nUse --device INDEX to select a microphone.")
            print("Use --list-devices to see all devices and exit.")
            return

        try:
            test_devices = sd.query_devices(args.device)
            if test_devices["max_input_channels"] == 0:
                raise RuntimeError(f"Device {args.device} does not support input.")
        except Exception as e:
            print(f"Warning: Problem with device {args.device}: {e}")
            # Auto-pick a likely microphone
            try:
                devices = sd.query_devices()
                preferred_keywords = ["microphone", "mic", "array"]
                candidate_idx = None
                for i, d in enumerate(devices):
                    name = (d.get("name") or "").lower()
                    if d.get("max_input_channels", 0) > 0 and any(
                        k in name for k in preferred_keywords
                    ):
                        candidate_idx = i
                        break
                if candidate_idx is None:
                    for i, d in enumerate(devices):
                        if d.get("max_input_channels", 0) > 0:
                            candidate_idx = i
                            break
                if candidate_idx is not None:
                    print(
                        f"Auto-selected input device {candidate_idx}: {devices[candidate_idx]['name']}"
                    )
                    args.device = candidate_idx
                else:
                    print("Error: No valid input devices found.")
                    return
            except Exception as e2:
                print(f"Error while auto-selecting microphone: {e2}")
                return

        q = queue.Queue()

        def audio_callback(indata, frames, time_info, status):
            if status:
                print(f"Audio status: {status}", file=sys.stderr)
            q.put(bytes(indata))

        print(f"Setting up audio stream with device {args.device}...")
        stream = sd.RawInputStream(
            samplerate=args.samplerate,
            blocksize=3000,
            device=args.device,
            dtype="int16",
            channels=1,
            latency="low",
            callback=audio_callback,
        )

    except Exception as e:
        print(f"Error initializing audio components: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you have a microphone connected")
        print("2. Check if another application is using the microphone")
        print("3. Try running with --list-devices to see available devices")
        print("4. On Windows, make sure Windows Audio service is running")
        return

    print("🎤 AssemblyAI Nutrition Assistant ready!")
    print(
        "💡 Say 'RYAN ...' before your question. Example: 'RYAN, how many calories in an apple?' "
    )
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
                        lower_text = text.lower()

                        # Allow global stop
                        if "stop listening" in lower_text or lower_text == "stop":
                            assistant.tts.speak("Okay, Have a great day. Bye bye.")
                            break

                        # Mid-speech interrupt ("stop" or "stop ryan")
                        if (
                            "stop ryan" in lower_text
                            or "ryan stop" in lower_text
                            or "stop" in lower_text
                        ) and assistant.tts.is_speaking():
                            assistant.tts.stop()
                            continue

                        # Wake-word gating: ignore all audio unless it contains the wake word
                        has_ryan = ("hey ryan" in lower_text) or ("ryan" in lower_text)
                        if not has_ryan:
                            # Do not print or speak anything; just keep listening
                            continue

                        try:
                            idx_hey_ryan = lower_text.find("hey ryan")
                            idx_ryan = lower_text.find("ryan")
                            indices = [i for i in [idx_hey_ryan, idx_ryan] if i != -1]
                            wake_index = min(indices) if indices else 0
                            phrase = (
                                "hey ryan"
                                if idx_hey_ryan != -1 and (wake_index == idx_hey_ryan)
                                else "ryan"
                            )
                            query_raw = text[wake_index + len(phrase) :]
                            query_raw = query_raw.lstrip(" ,.:;!?-")
                        except Exception:
                            query_raw = text

                        if not query_raw:
                            try:
                                assistant.tts.speak("Yes? Please ask your question.")
                            except Exception:
                                pass
                            continue

                        print(f"📝 You: {query_raw}")
                        reply = assistant.generate_reply(query_raw)
                        if not reply:
                            continue
                        if reply == "__STOP__":
                            assistant.tts.speak("Okay, Have a great day. Bye bye.")
                            break
                        try:
                            # Pause mic while speaking to avoid feedback and re-triggers
                            try:
                                stream.stop()
                            except Exception:
                                pass
                            print(f"🤖 Nutrition Assistant: {reply}")
                            assistant.tts.speak(reply)
                            # Wait for speech to finish (with a max cap)
                            wait_start = time.time()
                            while (
                                assistant.tts.is_speaking()
                                and (time.time() - wait_start) < 8.0
                            ):
                                time.sleep(0.05)
                        except Exception as e:
                            print(f"❌ TTS Error: {e}")
                        finally:
                            try:
                                stream.start()
                            except Exception:
                                pass
                    else:
                        # No final result yet; keep collecting audio
                        continue
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
        try:
            assistant.cleanup()
        except Exception:
            pass


if __name__ == "__main__":
    main()
