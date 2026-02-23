import uuid
from dataclasses import dataclass


@dataclass
class AudioFileMetadata:
    file_path: str
    file_name: str
    file_size: int
    file_hash: str
    audio_source_id: uuid.UUID
    initial_sr: float = None
    duration_ms: int = None
    channel_count: int = None
