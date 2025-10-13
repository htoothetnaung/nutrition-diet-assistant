python
import json
import os
import queue
import sys
import time

import numpy as np
import sounddevice as sd
import torch
from torch import nn
from torchaudio.transforms import Resample, MelSpectrogram, AmplitudeToDB

class KWSFeatures(nn.Module):
    def __init__(self, sample_rate=16000, n_mels=64):
        super().__init__()
        self.resample = Resample(orig_freq=sample_rate, new_freq=16000)
        self.mel = MelSpectrogram(sample_rate=16000, n_mels=n_mels)
        self.db = AmplitudeToDB()

    def forward(self, x):
        x = self.resample(x)
        x = self.mel(x)
        x = self.db(x)
        return x

class KWSCNN(nn.Module):
    def __init__(self, n_mels=64, n_classes=10):
        super().__init__()
        self.feats = KWSFeatures(n_mels=n_mels)
        self.net = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d((1,1)),
        )
        self.fc = nn.Linear(64, n_classes)

    def forward(self, x):
        x = self.feats(x)
        x = x.unsqueeze(1)
        x = self.net(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)

def main():
    if not os.path.exists("models/kws_cnn.pt"):
        print("Run training/train_keyword_spotter.py first.")
        sys.exit(1)
    labels = json.load(open("models/kws_labels.json"))
    model = KWSCNN(n_classes=len(labels))
    model.load_state_dict(torch.load("models/kws_cnn.pt", map_location="cpu"))
    model.eval()

    samplerate = 16000
    duration = 1.0  # seconds per clip
    blocksize = int(samplerate * duration)

    q = queue.Queue()
    def cb(indata, frames, time_info, status):
        if status: print(status, file=sys.stderr)
        q.put(np.frombuffer(indata, dtype=np.int16))

    with sd.RawInputStream(samplerate=samplerate, blocksize=blocksize, dtype="int16", channels=1, callback=cb):
        print("Listening 1-second clips. Ctrl+C to stop.")
        try:
            while True:
                data = q.get()
                wav = torch.from_numpy(data.astype(np.float32) / 32768.0).unsqueeze(0).unsqueeze(0)  # (1,1,T)
                with torch.no_grad():
                    logits = model(wav)
                    probs = torch.softmax(logits, dim=1)[0]
                    idx = int(torch.argmax(probs).item())
                    print(f"Predicted: {labels[idx]} (p={probs[idx].item():.2f})")
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
