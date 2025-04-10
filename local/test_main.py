import os
import boto3
import logging
from test_db import initialize_db, save_to_database
from test_logic import analyze_transcript
from test_stt import call_transcription_api

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def file_download(event, temp_file_path):
    print(f'file_download\n')

    record = event['Records'][0]
    bucket_name = record['s3']['bucket']['name']
    object_key = record['s3']['object']['key']
    if not bucket_name or not object_key:
        raise ValueError("Could not determine bucket name or object key from the event")

    print(f"Downloading from Bucket: {bucket_name}, Key: {object_key}\n")
    
    s3.download_file(bucket_name, object_key, temp_file_path)

def start_process(audio_filepath, db_filepath):
    conn = initialize_db(s3, db_filepath)
    transcript = call_transcription_api(audio_filepath)
    analysis = analyze_transcript(audio_filepath, transcript)
    save_to_database(conn, db_filepath, audio_filepath, transcript, analysis)

def lambda_handler(event, context):
    print(f'lambda_handler\n')
    print(f'event: {event}\n')
    print(f'context: {context}\n')

    audio_filename = os.path.basename(r'tmp_rec_audio.mp3')
    audio_temp_filepath = f"/tmp/{audio_filename}"
    
    db_filename = os.path.basename(r'transcriptions.db')
    db_temp_filepath = f"/tmp/{db_filename}"
    
    file_download(event, audio_temp_filepath)
    start_process(audio_temp_filepath, db_temp_filepath)
    
    return {
        "statusCode": 200, 
        "body": "Process completed successfully"
    }

if __name__ == "__main__":
    audio_filepath = r"data/recording_04042024151458.mp3"
    db_filepath = r"data/transcriptions.db"
    start_process(audio_filepath, db_filepath)