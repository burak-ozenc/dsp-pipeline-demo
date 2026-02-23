from datetime import datetime
from pathlib import Path

from prefect import flow

from config import config
from dsp.analyze import analyze_audio
from ingestion.discover import discover_files
from ml.vad import run_vad
from schema import AudioFileMetadata, AudioAnalytic, VADResult
from storage.loader import Loader


@flow
def process_audio_pipeline(source_dir: str):
    files = discover_files(source_dir)
    analytics_batch = []
    ml_label_batch = []

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
                vad_result = run_vad(file_path=file['file_path'],audio_file_id=new_audio_file_id)

                # add bulk insert for dsp analysis
                analytics_batch.append(
                    AudioAnalytic(
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
                    )
                )

                # 5. insert ml label
                ml_label_batch.append(VADResult(
                    audio_file_id=new_audio_file_id,
                    is_speech=vad_result.is_speech,
                    speech_confidence=vad_result.speech_confidence,
                ))

                if len(analytics_batch) >= 100:
                    try:
                        loader.bulk_insert_analytics(analytics_batch)
                        loader.bulk_insert_ml_labels(ml_label_batch)
                        for ml_label in analytics_batch:
                            loader.update_file_status(
                                file_id=ml_label.audio_file_id,
                                status='completed',
                                processed_at=datetime.now()
                            )
                    except Exception as e:
                        print("Failed to bulk insert analytics: {}".format(e))
                        for ml_label in analytics_batch:
                            loader.update_file_status(
                                file_id=ml_label.audio_file_id,
                                status='failed'
                            )
                        for ml_label in ml_label_batch:
                            loader.update_file_status(
                                file_id=ml_label.audio_file_id,
                                status='failed'
                            )
                    analytics_batch.clear()
                    ml_label_batch.clear()

                # 6. mark as completed
                # loader.update_file_status(file_id=new_audio_file_id, status='completed', processed_at=datetime.now())
                print("File processed {}".format(file['file_name']))

            except Exception as e:
                # mark as failed
                import traceback
                print("Error processing:", traceback.format_exc())
                print('Error occurred during processing file :' f'{file["file_path"]}')
                pass
        # flush remaining  analysis
        if analytics_batch:
            loader.bulk_insert_analytics(analytics_batch)    
        if ml_label_batch:
            loader.bulk_insert_ml_labels(ml_label_batch)    
        

