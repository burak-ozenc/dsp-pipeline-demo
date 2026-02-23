import torch
import numpy as np

from schema.vad_result import VADResult


model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    force_reload=False
)

get_speech_timestamps, _, read_audio, _, _ = utils

def run_vad(file_path: str) -> VADResult:
    audio = read_audio(file_path)

    window_size = 512  # samples (for 16kHz: 512 or 1536)

    confidences = []
    for i in range(0, len(audio) - window_size, window_size):
        chunk = audio[i: i + window_size]
        with torch.no_grad():
            confidence = model(chunk, 16000).item()  
        confidences.append(confidence)
        
    if not confidences:
        return VADResult(is_speech=False, speech_confidence=0.0)

    final_conf = float(np.average(confidences))
    
    res = VADResult(
        is_speech=final_conf > 0.5,
        speech_confidence=final_conf,
    )

    return res 