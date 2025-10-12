python
import argparse
import json
import os
from dataclasses import dataclass
from typing import List

import torch
import torchaudio
from torch import nn
from torch.utils.data import DataLoader
from torchaudio.datasets import SPEECHCOMMANDS
from torchaudio.transforms import Resample, MelSpectrogram, AmplitudeToDB

TARGET_LABELS = ["yes","no","up","down","left","right","on","off","stop","go"]

class SubsetSC(SPEECHCOMMANDS):
    def __init__(self, root, subset: str = None):
        super().__init__(root, download=True)
        def load_list(filename):
            filepath = os.path.join(self._path, filename)
            with open(filepath) as f:
                return [os.path.normpath(os.path.join(self._path, line.strip())) for line in f]
        if subset == "training":
            excludes = set(load_list("validation_list.txt") + load_list("testing_list.txt"))
            self._walker = [w for w in self._walker if w not in excludes]
        elif subset == "validation":
            self._walker = load_list("validation_list.txt")
        elif subset == "testing":
            self._walker = load_list("testing_list.txt")

    def __getitem__(self, n):
        waveform, sample_rate, label, *_ = super().__getitem__(n)
        return waveform, sample_rate, label

class KWSFeatures(nn.Module):
    def __init__(self, sample_rate=16000, n_mels=64):
        super().__init__()
        self.resample = Resample(orig_freq=sample_rate, new_freq=16000)
        self.mel = MelSpectrogram(sample_rate=16000, n_mels=n_mels)
        self.db = AmplitudeToDB()

    def forward(self, x):
        # x: (batch, 1, T)
        if x.shape[-1] == 0:
            return torch.zeros(x.shape[0], 64, 1, 1, device=x.device)
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
        # x: (batch, 1, T)
        x = self.feats(x)
        x = x.unsqueeze(1)  # (B, 1, n_mels, time)
        x = self.net(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)

def collate_fn(batch):
    xs, ys = [], []
    for waveform, sr, label in batch:
        if label not in TARGET_LABELS:
            continue
        xs.append(waveform.mean(dim=0, keepdim=True))  # mono
        ys.append(TARGET_LABELS.index(label))
    if not xs:
        return torch.zeros(0,1,16000), torch.zeros(0, dtype=torch.long)
    # Pad / crop to 1s (16000 samples)
    max_len = 16000
    padded = []
    for x in xs:
        if x.shape[-1] < max_len:
            pad = torch.zeros(1, max_len - x.shape[-1])
            x = torch.cat([x, pad], dim=-1)
        else:
            x = x[..., :max_len]
        padded.append(x)
    X = torch.stack(padded, dim=0)
    y = torch.tensor(ys, dtype=torch.long)
    return X, y

def accuracy(logits, y):
    if y.numel() == 0:
        return 0.0
    preds = logits.argmax(dim=1)
    return (preds == y).float().mean().item()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=str, default="data", help="Download/cache dir for SpeechCommands")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=1e-3)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    train_ds = SubsetSC(args.root, "training")
    val_ds = SubsetSC(args.root, "validation")

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, collate_fn=collate_fn)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, collate_fn=collate_fn)

    model = KWSCNN(n_classes=len(TARGET_LABELS)).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(1, args.epochs+1):
        model.train()
        total_loss = 0.0
        total_acc = 0.0
        n_batches = 0
        for X, y in train_loader:
            if X.shape[0] == 0:  # no labeled batch
                continue
            X = X.to(device)
            y = y.to(device)
            opt.zero_grad()
            logits = model(X)
            loss = criterion(logits, y)
            loss.backward()
            opt.step()
            total_loss += loss.item()
            total_acc += accuracy(logits, y)
            n_batches += 1
        if n_batches == 0:
            print("No batches this epoch; try running again to let dataset finish downloading.")
            continue
        avg_loss = total_loss / n_batches
        avg_acc = total_acc / n_batches

        # Validation
        model.eval()
        with torch.no_grad():
            val_accs = []
            for X, y in val_loader:
                if X.shape[0] == 0: continue
                X = X.to(device); y = y.to(device)
                logits = model(X)
                val_accs.append(accuracy(logits, y))
            val_acc = sum(val_accs)/len(val_accs) if val_accs else 0.0

        print(f"Epoch {epoch}: train_loss={avg_loss:.4f} train_acc={avg_acc:.3f} val_acc={val_acc:.3f}")

    os.makedirs("models", exist_ok=True)
    torch.save(model.state_dict(), "models/kws_cnn.pt")
    with open("models/kws_labels.json", "w") as f:
        json.dump(TARGET_LABELS, f)
    print("Saved models/kws_cnn.pt and models/kws_labels.json")

if __name__ == "__main__":
    main()
