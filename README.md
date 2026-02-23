# Audio Analytics Pipeline Demo
Purpose is to create a pipeline over Prefect, extract basic DSP features from a sample music-speech-noise dataset, analyze, label and send it to pipeline.


For now analyses includes:
- snr_db
- clipping_ratio
- max_amplitude
- dynamic_range
- signal_to_quantization_ratio
- band_energy_ratio
- spectral_centroid_mean
- zcr_std
- zcr_mean
- silence_ratio
- bandwidth_mean
- bandwidth_std

## Notes
Using 16 bit depth for all samples for consistency
FFmpeg pre-processing planned for multi format support 