import argparse
import json
import queue
import sys
print(sys.executable)
import time

import sounddevice as sd
from utils.stt_vosk import VoskSTT
from utils.tts_pyttsx3 import TTS

def generate_reply(text: str) -> str:
    """Very simple rule-based AI reply."""
    t = text.lower().strip()

    if t in {"hi", "hello", "hey"} or any(x in t for x in ["good morning", "good evening", "good afternoon"]):
        return "Hello! How can I help you?"

    if "your name" in t:
        return "I'm your local voice assistant."

    if "time" in t:
        return time.strftime("It's %I:%M %p.")

    if "date" in t or "day" in t:
        return time.strftime("Today is %A, %B %d, %Y.")

    if "stop listening" in t or t == "stop":
        return "__STOP__"

    if t:
        return f"You said: {text}"
    return ""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True, help="Path to Vosk model folder")
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
        # Initialize TTS & STT
        print("Initializing TTS...")
        tts = TTS()
        print("Initializing STT...")
        stt = VoskSTT(model_path=args.model, samplerate=args.samplerate)

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

    print("🎤 Starting mic. Speak to me! Say 'stop listening' to exit.\n")
    try:
        with stream:
            while True:
                try:
                    data = q.get()
                    if stt.accept_waveform(data):
                        result = stt.get_result()
                        text = result.get("text", "").strip()
                        if not text:
                            continue
                        print(f"📝 You: {text}")

                        reply = generate_reply(text)
                        if not reply:
                            continue

                        if reply == "__STOP__":
                            tts.speak("Okay, I will stop listening now. Goodbye!")
                            break

                        # Avoid feedback: pause mic while speaking
                        stream.stop()
                        try:
                            print(f"🤖 Assistant: {reply}")
                            tts.speak(reply)
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
        # Clean up TTS
        try:
            tts.cleanup()
        except:
            pass

if __name__ == "__main__":
    main()
