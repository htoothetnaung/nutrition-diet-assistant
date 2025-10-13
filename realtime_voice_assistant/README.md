# Real‑Time Speech Assistant (Python, VS Code)

This starter gives you **real-time speech recognition** (offline, using Vosk) and **voice replies** (offline, using `pyttsx3`).  
It also includes a tiny **keyword‑spotting training example** (using PyTorch + SpeechCommands).

---

## 1) Set up (Windows/macOS/Linux)

1. Install Python 3.9–3.12.
2. In VS Code, open this project folder.
3. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   > If PyTorch fails to install, follow the official PyTorch install page for your OS/GPU. You can still run the real‑time assistant without the training example.

5. **Download a Vosk English model** (e.g., `vosk-model-small-en-us-0.15`), unzip it, and put the folder inside `models/`.  
   Your path should look like: `models/vosk-model-small-en-us-0.15`.

---

## 2) Run the real-time voice assistant

```bash
python app.py --model models/vosk-model-small-en-us-0.15 --device 0
```
- `--device` is the microphone index; `0` is often default. If you have multiple mics, try other numbers.
- Say things like **“hello”**, **“what time is it”**, **“what’s today’s date”**, or **“stop listening”**.
- The assistant **talks back** using your system’s default voice.

> Tip: If the assistant hears itself while speaking, it will temporarily **pause** the microphone to avoid feedback.

---

## 3) (Optional) Train a tiny keyword‑spotter

This trains a small CNN on a subset of **SpeechCommands** (yes/no/up/down/left/right/on/off/stop/go).

```bash
# Train (downloads a few GB; you may cancel after small subset downloads)
python training/train_keyword_spotter.py --epochs 3 --batch-size 64

# Try the trained model on microphone audio (short 1s clips)
python training/kws_infer.py
```

Artifacts saved to:
- `models/kws_labels.json`
- `models/kws_cnn.pt`

You can combine this with the assistant to robustly detect a keyword like **“stop”** even if full ASR mishears it.

---

## 4) Files

- `app.py` — real‑time Vosk STT + pyttsx3 TTS, with simple rule‑based replies.
- `utils/stt_vosk.py` — Vosk recognizer wrapper.
- `utils/tts_pyttsx3.py` — pyttsx3 text‑to‑speech wrapper.
- `training/train_keyword_spotter.py` — KWS training on SpeechCommands.
- `training/kws_infer.py` — test the KWS model on mic audio.
- `requirements.txt` — dependencies.

---

## 5) Troubleshooting

- **No audio / wrong mic**: change `--device` or remove it to list available devices printed at start.
- **Assistant hears itself**: it temporarily stops the mic while speaking; if you still get feedback, lower speakers or use headphones.
- **PyTorch install issues**: skip training; the assistant itself doesn’t need PyTorch.

Enjoy! 🎤🔊


//py app.py --model "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15" --device 5


//py gemini_nutrition_assistant.py --model "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15" --device 0 --gemini-key "AIzaSyAEMVxZwA3agXSD1_Hw1G23zQexOYgOZ2U"


//py gemini_nutrition_assistant.py --model "vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15" --device 1  --gemini-key "$env:GEMINI_API_KEY"

fsfsf