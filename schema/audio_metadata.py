from dataclasses import dataclass
from enum import Enum


@dataclass
class AudioFileMetadata:
    file_path: str
    file_name: str
    file_size: int
    file_hash: str
    audio_source_id: str
    initial_sr: float = None
    duration_ms: int = None
    channel_count: int = None


class FoobarEnum(str, Enum):
    FIRST = "foobar"
    SECOND = "baz"
