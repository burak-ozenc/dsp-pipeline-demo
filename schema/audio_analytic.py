from dataclasses import dataclass
from typing import Optional

@dataclass
class AudioAnalytic:

    snr_db: Optional[float] = None
    clipping_ratio: Optional[float] = None
    max_amplitude: Optional[float] = None
    dynamic_range: Optional[float] = None
    signal_to_quantatization_ratio: Optional[float] = None
    band_energy_ratio: Optional[float] = None
    spectral_centroid_mean: Optional[float] = None
    zcr_std: Optional[float] = None
    zcr_mean: Optional[float] = None
    silence_ratio: Optional[float] = None
    bandwith_mean: Optional[float] = None
    bandwith_std: Optional[float] = None
    source_type: str = "" # ?
