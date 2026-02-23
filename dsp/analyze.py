import librosa
import numpy as np

from schema.audio_analytic import AudioAnalytic

def analyze_audio(file_path: str) -> AudioAnalytic:
    """
    We will extract some features from given audio(path):
    
    """
    y, sr = librosa.load(file_path,sr=16000) # standard sr across all data

    zcr_std, zcr_mean = calc_zcr(audio=y)
    bw_mean, bw_std = calc_bandwidth(audio=y)

    analytics = AudioAnalytic(
        snr_db=calc_snr(audio=y),
        clipping_ratio=calc_clipping_ratio(audio=y),
        max_amplitude=calc_max_amplitude(audio=y),
        dynamic_range=calc_dynamic_range(audio=y),
        signal_to_quantatization_ratio=calc_signal_to_quantization_noise_ratio(audio=y),
        band_energy_ratio=calc_band_energy_ratio(audio=y,sr=sr),
        spectral_centroid_mean=calc_spectral_centroid_mean(y),
        zcr_std=zcr_std,
        zcr_mean=zcr_mean,
        silence_ratio=calc_silence_ratio(audio=y),
        bandwith_mean=bw_mean,
        bandwith_std=bw_std,
    )

    return analytics


def calc_clipping_ratio(audio):
    threshold = 0.99
    clipped_samples = np.sum(np.abs(audio) >= threshold)
    clipping_ratio = clipped_samples / audio.size

    return safe_float(clipping_ratio)


def calc_zcr(audio) -> tuple[float, float]:
    zcr = librosa.feature.zero_crossing_rate(audio)[0]
    zcr_mean = np.mean(zcr)
    zcr_std = np.std(zcr)
    
    return safe_float(zcr_std), safe_float(zcr_mean) 


def calc_rms_mean(audio):
    rms = librosa.feature.rms(y=audio)[0]
    rms_mean = np.mean(rms)

    return safe_float(rms_mean)


def calc_spectral_centroid_mean(audio):
    spectral_centroid = librosa.feature.spectral_centroid(y=audio)[0]
    spectral_centroid_mean = np.mean(spectral_centroid)

    return safe_float(spectral_centroid_mean)


def calc_silence_ratio(audio):
    """
    we assume that silence ratio something like 5 percent of max rms 
    """
    rms = librosa.feature.rms(y=audio)[0]
    max_rms = np.max(rms)
    threshold = max_rms * 0.05
    silence_ratio = np.sum(rms < threshold) / len(rms)

    return safe_float(silence_ratio)


def calc_max_amplitude(audio):
    max_amplitude = np.max(audio)

    return safe_float(max_amplitude)


def calc_snr(audio):
    """
    we assume that noise ratio is something like 10 percent of max rms  
    """
    rms = librosa.feature.rms(y=audio)[0]
    # noise threshold
    noise_threshold = np.percentile(rms, 10)
    noise_frames = rms[rms <= noise_threshold]
    noise_power = np.mean(noise_frames ** 2)
    # signal threshold
    signal_frames = rms[rms > noise_threshold]
    signal_power = np.mean(signal_frames ** 2)
    # null check
    if len(noise_frames) == 0 or len(signal_frames) == 0:
        return np.nan

    sound_to_noise_ratio = 10 * np.log10(signal_power / noise_power)

    return safe_float(sound_to_noise_ratio) 


def calc_dynamic_range(audio):
    max_amplitude = np.max(audio)
    # watch out for complete silence
    min_amplitude = np.percentile(np.abs(audio), 1)
    dynamic_range_db = 10 * np.log10(np.abs(max_amplitude / min_amplitude))

    return safe_float(dynamic_range_db) 


def calc_signal_to_quantization_noise_ratio(audio):
    # max signal strength / quantization error ratio
    signal_rms = np.sqrt(np.mean(audio ** 2))

    # this is the main formula for SQNR
    # 6.02~ is 20xlog10(2) , each additional bit doubles the quantization level(2**N), approx. 6dB
    # 1.76 and np.sqrt(12) are statistical properties
    # quantization_step = 1 / ((6.02 * 16 * 1.76) / 2)
    # quantization_noise_rms = quantization_step / np.sqrt(12) 
    # 32768 is standard and half of the 65536, which is 2^16, CDs are 16 bits
    quantization_step = 1.0 / 32768
    quantization_noise_rms = quantization_step / np.sqrt(12)

    sqnr_db = 10 * np.log10((signal_rms / quantization_noise_rms) ** 2)

    return safe_float(sqnr_db) 


def calc_bandwidth(audio) -> tuple[float, float]:
    bandwidth = librosa.feature.spectral_bandwidth(y=audio,sr=16000)
    bandwidth_mean = np.mean(bandwidth)
    bandwidth_std = np.std(bandwidth)

    return safe_float(bandwidth_mean) , safe_float(bandwidth_std)


def calc_band_energy_ratio(audio, sr):
    """
    we will use low/high as band energy ratio 
    """
    D = librosa.stft(audio)
    magnitude = np.abs(D) ** 2
    # frequency bins - lows- mids - highs
    frequencies = librosa.fft_frequencies(sr=sr)
    low_band_mask = frequencies <= 2000
    high_band_mask = frequencies > 2000
    # calc energies given dimensions
    low_band_energy = np.sum(magnitude[low_band_mask, :])
    high_band_energy = np.sum(magnitude[high_band_mask, :])
    # just to be sure
    if high_band_energy == 0:
        return 0
    band_energy_ratio = low_band_energy / high_band_energy
    band_energy_ratio_db = 10 * np.log10(band_energy_ratio)

    return safe_float(band_energy_ratio_db)

# helper to handle edge cases Infinity or Nan
def safe_float(value) -> float | None:
    if value is None:
        return None
    if np.isinf(value) or np.isnan(value):
        return None
    return float(value)