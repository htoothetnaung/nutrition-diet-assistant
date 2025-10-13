
import json
from vosk import Model, KaldiRecognizer

class VoskSTT:
    def __init__(self, model_path: str, samplerate: int = 16000):
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, samplerate)

    def accept_waveform(self, pcm_bytes: bytes) -> bool:
        """Feed PCM int16 mono @ 16k to the recognizer.
        Returns True when a final result is ready.
        """
        return self.recognizer.AcceptWaveform(pcm_bytes)

    def get_result(self) -> dict:
        return json.loads(self.recognizer.Result())

    def get_partial(self) -> dict:
        return json.loads(self.recognizer.PartialResult())
