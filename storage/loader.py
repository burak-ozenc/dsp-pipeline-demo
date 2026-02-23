from uuid import UUID

import psycopg

from dotenv import load_dotenv
load_dotenv()

from config.config import config
from schema import AudioAnalytic, VADResult
from schema.audio_metadata import AudioFileMetadata


class Loader:
    def __init__(self):
        self.conn_str = config.CONNECTION_STRING
        self.conn = None

    def __enter__(self):
        self.conn = psycopg.connect(self.conn_str)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f'{exc_type}: {exc_val}')
        if self.conn:
            self.conn.close()

        return False

    def get_or_create_audio_source(self, source_name: str) -> UUID:
        # try to find existing
        with self.conn.cursor() as cursor:
            cursor.execute('select id '
                           'from audio_sources '
                           'where audio_source_name = %s ',
                           (source_name,))

            row = cursor.fetchone()
            if row is not None:
                return row[0]
            # if not found, insert and return new id
            else:
                cursor.execute('insert into audio_sources '
                               '(audio_source_name) '
                               'values (%s) '
                               'returning id;',
                               (source_name,))
                new_id = cursor.fetchone()[0]
                self.conn.commit()
                return new_id

    def get_file_status(self, file_hash) -> str | None:
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT status '
                           'FROM audio_files '
                           'WHERE file_hash = %s', (file_hash,))
            row = cursor.fetchone()
            return row[0] if row else None

    def get_or_insert_audio_file(self, metadata: AudioFileMetadata):
        with self.conn.cursor() as cursor:
            cursor.execute('select id '
                           'from audio_files '
                           'where file_hash = %s ',
                           (metadata.file_hash,))

            row = cursor.fetchone()
            if row is not None:
                return row[0]
            # if not found, insert and return new id
            else:
                cursor.execute('insert into audio_files('
                               'file_path, file_name, file_size, file_hash,'
                               ' audio_source_id, initial_sr, duration_ms, channel_count'
                               ') '
                               'values (%s, %s, %s, %s, %s, %s, %s, %s) '
                               'returning id;',
                               (metadata.file_path, metadata.file_name, metadata.file_size, metadata.file_hash,
                                metadata.audio_source_id, metadata.initial_sr, metadata.duration_ms,
                                metadata.channel_count))
                new_id = cursor.fetchone()[0]
                self.conn.commit()
    
                return new_id

    def insert_audio_analytics(self, analytic: AudioAnalytic):
        with self.conn.cursor() as cursor:
            cursor.execute('insert into audio_analytics('
                           'audio_file_id, audio_source_id, snr_db,clipping_ratio,max_amplitude,dynamic_range,'
                           'signal_to_quantatization_ratio,band_energy_ratio,spectral_centroid_mean,zcr_std,zcr_mean,'
                           'silence_ratio,bandwith_mean,bandwith_std,source_type'
                           ') '
                           'values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);',
                           (analytic.audio_file_id, analytic.audio_source_id, analytic.snr_db, analytic.clipping_ratio,
                            analytic.max_amplitude, analytic.dynamic_range, analytic.signal_to_quantatization_ratio,
                            analytic.band_energy_ratio, analytic.spectral_centroid_mean, analytic.zcr_std,
                            analytic.zcr_mean, analytic.silence_ratio, analytic.bandwith_mean,
                            analytic.bandwith_std, analytic.source_type,))

            self.conn.commit()

    def bulk_insert_analytics(self, analytics: list[AudioAnalytic]):
        with self.conn.cursor() as cursor:
            with cursor.copy(
                    "COPY audio_analytics("
                    "audio_file_id, audio_source_id, snr_db,clipping_ratio,max_amplitude,dynamic_range,"
                    "signal_to_quantatization_ratio,band_energy_ratio,spectral_centroid_mean,zcr_std,zcr_mean,"
                    "silence_ratio,bandwith_mean,bandwith_std,source_type"
                    ") FROM STDIN "
            ) as copy:
                for analytic in analytics:
                    copy.write_row((
                        analytic.audio_file_id, analytic.audio_source_id, analytic.snr_db, analytic.clipping_ratio,
                        analytic.max_amplitude, analytic.dynamic_range, analytic.signal_to_quantatization_ratio,
                        analytic.band_energy_ratio, analytic.spectral_centroid_mean, analytic.zcr_std,
                        analytic.zcr_mean, analytic.silence_ratio, analytic.bandwith_mean,
                        analytic.bandwith_std, analytic.source_type,
                    ))
        self.conn.commit()

    def insert_ml_label(self, vad_result: VADResult):
        with self.conn.cursor() as cursor:
            cursor.execute('insert into ml_labels('
                           'audio_file_id, is_speech, speech_confidence'
                           ') '
                           'values (%s, %s, %s);',
                           (vad_result.audio_file_id, vad_result.is_speech, vad_result.speech_confidence))
            self.conn.commit()

    def bulk_insert_ml_labels(self, vad_results: list[VADResult]):
        with self.conn.cursor() as cursor:
            with cursor.copy(
                    "COPY ml_labels("
                    "audio_file_id, is_speech, speech_confidence"
                    ") FROM STDIN "
            ) as copy:
                for vad_result in vad_results:
                    copy.write_row((
                        vad_result.audio_file_id, vad_result.is_speech, vad_result.speech_confidence
                    ))
        self.conn.commit()

    def update_file_status(self, file_id: UUID, status: str, processed_at=None):
        with self.conn.cursor() as cursor:
            if processed_at:
                cursor.execute('UPDATE audio_files '
                               'SET status = %s, processed_at = %s '
                               'WHERE id = %s',
                               (status, processed_at, file_id))
            else:
                cursor.execute('UPDATE audio_files '
                               'SET status = %s '
                               'WHERE id = %s',
                               (status, file_id))

            self.conn.commit()