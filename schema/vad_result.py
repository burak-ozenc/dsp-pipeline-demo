from dataclasses import dataclass
from uuid import UUID


@dataclass
class VADResult:
    audio_file_id: UUID
    is_speech: bool
    speech_confidence: float