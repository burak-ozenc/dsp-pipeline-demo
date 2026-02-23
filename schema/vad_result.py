from dataclasses import dataclass


@dataclass
class VADResult:
    is_speech: bool
    speech_confidence: float