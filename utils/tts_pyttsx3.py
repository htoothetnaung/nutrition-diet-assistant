
import pyttsx3
import threading
import time
import re
import os

class TTS:
    def __init__(self, rate: int = 180):
        self.rate = rate
        self._lock = threading.RLock()
        self._engine = None
        self._thread = None
        print(f"TTS initialized with rate: {self.rate}")

    def _ensure_engine(self):
        """Create or reuse a single engine and configure voice/rate."""
        if self._engine is not None:
            return self._engine
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", 1.0)
            # Prefer configured voice via env vars
            requested_name = os.environ.get("TTS_VOICE_NAME", "").strip()
            requested_id = os.environ.get("TTS_VOICE_ID", "").strip()
            voices = engine.getProperty("voices") or []
            def set_voice_by(predicate):
                for v in voices:
                    if predicate(v):
                        try:
                            engine.setProperty("voice", v.id)
                            return True
                        except Exception:
                            continue
                return False
            if requested_id:
                set_voice_by(lambda v: v.id == requested_id)
            elif requested_name:
                lowered = requested_name.lower()
                set_voice_by(lambda v: lowered in (v.name or "").lower())
            else:
                # Prefer well-known Windows male voice if present
                if not set_voice_by(lambda v: (v.name or "").lower() == "Microsoft David Desktop".lower()):
                    # Prefer male-sounding names
                    preferred_male_keys = ["david", "mark", "alex", "barry", "george", "male"]
                    if not set_voice_by(lambda v: any(k in (v.name or "").lower() for k in preferred_male_keys)):
                        # Fallback to first
                        if voices:
                            try:
                                engine.setProperty("voice", voices[0].id)
                            except Exception:
                                pass
            self._engine = engine
        except Exception as e:
            print(f"Error creating TTS engine: {e}")
            self._engine = None
        return self._engine

    def _chunk_text(self, text: str, max_len: int = 300):
        # Split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text.strip()) if text else []
        chunks = []
        current = ""
        for s in sentences:
            if len(current) + len(s) + 1 <= max_len:
                current = (current + " " + s).strip()
            else:
                if current:
                    chunks.append(current)
                # If sentence itself longer than max, split hard
                if len(s) > max_len:
                    for i in range(0, len(s), max_len):
                        chunks.append(s[i:i+max_len])
                    current = ""
                else:
                    current = s
        if current:
            chunks.append(current)
        if not chunks and text:
            chunks = [text]
        return chunks

    def _speak_with_engine(self, engine, text: str):
        # Queue chunks and run
        for chunk in self._chunk_text(text):
            engine.say(chunk)
        # Guard run loop already started by ensuring no concurrent runAndWait
        try:
            engine.runAndWait()
        except RuntimeError as e:
            # Attempt to stop and retry once
            try:
                engine.stop()
            except Exception:
                pass
            time.sleep(0.05)
            engine.runAndWait()

    def _retry_with_other_voices(self, text: str) -> bool:
        """Try cycling through installed voices to find a working one."""
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", 1.0)
            voices = engine.getProperty("voices") or []
            for voice in voices:
                try:
                    engine.setProperty("voice", voice.id)
                    self._speak_with_engine(engine, text)
                    print("✅ Speech completed (fallback voice)")
                    self._engine = engine
                    return True
                except Exception as e:
                    print(f"⚠️ Voice '{getattr(voice,'name',voice.id)}' failed: {e}")
                    continue
        except Exception as e:
            print(f"❌ Could not initialize fallback engine: {e}")
        return False

    def _worker(self, text: str):
        try:
            engine = self._ensure_engine()
            if not engine:
                print(f"❌ TTS engine failed, would say: {text}")
                return
            print(f"🔊 Speaking: {text}")
            try:
                self._speak_with_engine(engine, text)
                print("✅ Speech completed")
            except Exception as e:
                print(f"⚠️ TTS run error, retrying with fresh engine/voices: {e}")
                # Retry with fresh engine and other voices
                self._engine = None
                if not self._retry_with_other_voices(text):
                    print(f"❌ TTS engine failed, would say: {text}")
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            print(f"Would say: {text}")
        finally:
            with self._lock:
                self._thread = None

    def say(self, text: str):
        """Speak the given text synchronously with strong guards (no overlapping run loops)."""
        if not text or not text.strip():
            return
        with self._lock:
            # Interrupt current speech if any
            try:
                self._ensure_engine()
                if self._engine:
                    self._engine.stop()
            except Exception:
                pass
            # Run worker inline (blocking) to avoid concurrent run loops
            self._thread = None
            self._worker(text)

    def speak(self, text: str):
        """Alias for say method for compatibility."""
        self.say(text)
    
    def stop(self):
        """Stop any ongoing speech immediately."""
        with self._lock:
            try:
                self._ensure_engine()
                if self._engine:
                    self._engine.stop()
            except Exception:
                pass

    def is_speaking(self) -> bool:
        with self._lock:
            try:
                self._ensure_engine()
                if self._engine and hasattr(self._engine, 'isBusy'):
                    return bool(self._engine.isBusy())
            except Exception:
                pass
            return False
    
    def cleanup(self):
        """Clean up the TTS engine."""
        with self._lock:
            try:
                if self._engine:
                    self._engine.stop()
            except Exception:
                pass
            self._engine = None