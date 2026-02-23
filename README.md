# Audio Analytics Pipeline Demo
Purpose is to create a pipeline over Prefect, extract basic DSP features from a sample music-speech-noise dataset, analyze, label and send it to pipeline.

## Overview:
- to create an ETL pipeline and to run over Prefect
- extract and analyze basic DSP features with Librosa and Numpy from a sample music-speech-noise dataset from [MUSAN](https://openslr.org/17),
- extract confidence score with Silero VAD

## Flow
```
 1- INGEST 	- discover '*.wav' files within given data path, hash an return the file[] 
 2- ANALYZE - load the audio files from path, apply basic DSP analyses over them
 3- LABEL 	- extract speech confidence using Silero VAD, and label audio files
 4- PERSIST - persist the data to PostgreSQL using bulk COPY inserts
```


## Schema Design Decisions
- file_hash based idempotency: file paths break when data moves, hashes don''t. re-running the pipeline on the same dataset is safe
- since we are using already pre-defined sets by MUSAN, it makes more sense to create partition by source type
- audio_analytics partitioned by source_type: queries almost always filter by source category. partition pruning eliminates irrelevant partitions without touching indexes
- created indexes for most possible needed fields like snr_db, silence_ratio, speech_confidence
- used bulk COPY due to performance improvements


## DSP Results
- speech has the highest signal-to-noise ratio(38.1 dB)
- noise files show 60x more clipping ratio than speech/music
- VAD achieved 99.6% accuracy, almost zero false positives on noise, 3.9% false positive on music, most likely vocal content
- 5 noise files identified as problematic: high clipping_ratio with low snr_db

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


## Scaling Considerations

current implementation handles thousands of files efficiently. at TB scale the following changes would be necessary:

- **Parallel processing**: replace sequential file loop with  multiprocessing. pool to utilize multiple CPU cores for DSP analysis
- **Connection pooling**: pgBouncer between the pipeline and PostgreSQL to handle concurrent workers without exhausting connections
- **Bulk loading**: already implemented via PostgreSQL COPY, at scale this becomes critical (a lot faster than row-by-row INSERT)
- **Partitioning strategy**: add time-based partitioning alongside source_type for efficient time-range queries on large datasets
- **FFmpeg preprocessing**: normalize heterogeneous audio formats before ingestion — essential when ingesting from multiple real-world sources
- **Distributed orchestration**: Prefect''s work pools support distributed execution across multiple machines