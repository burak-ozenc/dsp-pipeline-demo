CREATE TYPE process_status
    AS
    ENUM('pending', 'processing', 'completed', 'failed');



CREATE TABLE audio_sources
(
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audio_source_name TEXT NOT NULL,
    created_at        TIMESTAMPTZ      DEFAULT NOW()
);


CREATE TABLE audio_files
(
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audio_source_id UUID NOT NULL,
    initial_sr      FLOAT,
    file_name       TEXT NOT NULL,
    file_path       TEXT NOT NULL,
    duration_ms     INTEGER,
    file_size       BIGINT,
    channel_count   INTEGER,
    status          process_status   DEFAULT 'pending',
    created_at      TIMESTAMPTZ      DEFAULT NOW(),
    processed_at    TIMESTAMPTZ,
    file_hash       TEXT NOT NULL,
    CONSTRAINT fk_audio_files_audio_source_id
        FOREIGN KEY (audio_source_id)
            REFERENCES audio_sources (id),
    UNIQUE (file_path),
    UNIQUE (file_hash)
);



CREATE TABLE audio_analytics
(
    id                             UUID        DEFAULT gen_random_uuid(),
    audio_file_id                  UUID NOT NULL,
    audio_source_id                UUID NOT NULL,
    snr_db                         FLOAT,
    clipping_ratio                 FLOAT,
    max_amplitude                  FLOAT,
    dynamic_range                  FLOAT,
    signal_to_quantatization_ratio FLOAT,
    band_energy_ratio              FLOAT,
    spectral_centroid_mean         FLOAT,
    zcr_std                        FLOAT,
    zcr_mean                       FLOAT,
    silence_ratio                  FLOAT,
    bandwith_mean                  FLOAT,
    bandwith_std                   FLOAT,
    created_at                     TIMESTAMPTZ DEFAULT NOW(),
    source_type                    TEXT NOT NULL,
    PRIMARY KEY (id, source_type),
    CONSTRAINT fk_analytics_audio_file
        FOREIGN KEY (audio_file_id)
            REFERENCES audio_files (id),
    CONSTRAINT fk_analytics_audio_source_id
        FOREIGN KEY (audio_source_id)
            REFERENCES audio_sources (id)
) PARTITION BY LIST (source_type);



CREATE TABLE audio_analytics_music
    PARTITION OF audio_analytics FOR VALUES IN
(
    'music'
);
CREATE TABLE audio_analytics_speech
    PARTITION OF audio_analytics FOR VALUES IN
(
    'speech'
);
CREATE TABLE audio_analytics_noise
    PARTITION OF audio_analytics FOR VALUES IN
(
    'noise'
);



CREATE TABLE ml_labels
(
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audio_file_id     UUID NOT NULL,
    is_speech         BOOLEAN,
    speech_confidence FLOAT,
    created_at        TIMESTAMPTZ      DEFAULT NOW(),
    CONSTRAINT fk_ml_labels_audio_file
        FOREIGN KEY (audio_file_id)
            REFERENCES audio_files (id)
);



CREATE INDEX idx_audio_files_status ON audio_files (status);


CREATE INDEX idx_audio_files_source_id ON audio_files (audio_source_id);
CREATE INDEX idx_analytics_audio_file_id ON audio_analytics (audio_file_id);



CREATE INDEX idx_audio_analytics_clipping_ratio ON audio_analytics (clipping_ratio);
CREATE INDEX idx_audio_analytics_snr_db ON audio_analytics (snr_db);
CREATE INDEX idx_audio_analytics_silence_ratio ON audio_analytics (silence_ratio);

CREATE INDEX idx_ml_labels_audio_file_id ON ml_labels (audio_file_id);
CREATE INDEX idx_ml_labels_speech_confidence ON ml_labels (speech_confidence);