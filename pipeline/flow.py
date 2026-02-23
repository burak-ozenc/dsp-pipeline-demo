from datetime import datetime
from pathlib import Path

from prefect import flow

from config import config
from dsp.analyze import analyze_audio
from ingestion.discover import discover_files
from ml.vad import run_vad
from schema import AudioFileMetadata, AudioAnalytic
from storage.loader import Loader


@flow
def process_audio_pipeline(source_dir: str):
    files = discover_files(source_dir)

    with Loader() as loader:
        for file in files:
            try:
                status = loader.get_file_status(file['file_hash'])
                if status == 'completed':
                    continue
                    
                source_type = Path(file['file_path']).parts[3]
                audio_source_id = loader.get_or_create_audio_source(source_type)    
                # 1. insert file record, mark as processing
                new_audio_file_id = loader.insert_audio_file(AudioFileMetadata(
                    file_path=file['file_path'],
                    file_name=file['file_name'],
                    file_size=file['file_size'],
                    file_hash=file['file_hash'],
                    audio_source_id=audio_source_id,
                ))
                loader.update_file_status(file_id=new_audio_file_id, status='processing')

                # 2. run dsp analysis
                analysis = analyze_audio(file_path=file['file_path'])

                # 3. run vad
                vad_result = run_vad(file_path=file['file_path'])

                # 4. insert analytics
                loader.insert_audio_analytics(AudioAnalytic(
                    audio_source_id=audio_source_id,
                    audio_file_id=new_audio_file_id,
                    snr_db=analysis.snr_db,
                    clipping_ratio=analysis.clipping_ratio,
                    max_amplitude=analysis.max_amplitude,
                    dynamic_range=analysis.dynamic_range,
                    signal_to_quantatization_ratio=analysis.signal_to_quantatization_ratio,
                    band_energy_ratio=analysis.band_energy_ratio,
                    spectral_centroid_mean=analysis.spectral_centroid_mean,
                    zcr_std=analysis.zcr_std,
                    zcr_mean=analysis.zcr_mean,
                    silence_ratio=analysis.silence_ratio,
                    bandwith_mean=analysis.bandwith_mean,
                    bandwith_std=analysis.bandwith_std,
                    source_type=source_type,
                ))

                # 5. insert ml label
                loader.insert_ml_label(vad_result=vad_result, audio_file_id=new_audio_file_id)
                
                # 6. mark as completed
                loader.update_file_status(file_id=new_audio_file_id, status='completed',processed_at=datetime.now())
                

            except Exception as e:
                # mark as failed
                # import traceback
                # print("Error processing:", traceback.format_exc())
                print('Error occurred during processing file :' f'{file["file_path"]}')
                pass

