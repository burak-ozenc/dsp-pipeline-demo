import psycopg

from config import config
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

    def check_file_exists(self, file_hash) -> bool:
        with self.conn.cursor() as cursor:
            cursor.execute('select 1 '
                           'from audio_files '
                           'where file_hash = %s',
                           (file_hash,))

            return cursor.fetchone() is not None

    def insert_audio_file(self, metadata :AudioFileMetadata):
        with self.conn.cursor() as cursor:
            cursor.execute('insert into audio_files('
                           'file_path, file_name, file_size, file_hash,'
                           ' audio_source_id, initial_sr, duration_ms, channel_count'
                           ') '
                           'values (%s, %s, %s, %s, %s, %s, %s, %s)',
                           (metadata.file_path, metadata.file_name, metadata.file_size, metadata.file_hash,
                            metadata.audio_source_id, metadata.initial_sr, metadata.duration_ms,
                            metadata.channel_count ))
            self.conn.commit()

    def update_file_status(self, file_id: str, status: str, processed_at=None):
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


check_file_exists('0bb1a5c6e5467cbf129d3fe8c80fc4ff')
