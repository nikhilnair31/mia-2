import boto3
from test_db import initialize_db, save_to_database
from test_logic import analyze_transcript
from test_stt import call_transcription_api

s3 = boto3.client('s3')

def file_download(event, download_path):
    bucket_name = 'your-bucket-name'  # Replace with your bucket name
    object_key = 'path/to/your/audio.mp3'  # Replace with your object key

    # Check if this is an S3 event
    if 'Records' in event and len(event['Records']) > 0:
        record = event['Records'][0]
        if 'S3' in record:
            bucket_name = record['s3']['bucket']['name'],
            object_key = record['s3']['object']['key']
    # If no S3 event, check for direct parameters
    elif 'bucket' in event and 'key' in event:
        bucket_name = event['bucket'],
        object_key = event['key']
    
    s3.download_file(bucket_name, object_key, download_path)

def start_process(audio_filepath, db_filepath):
    conn = initialize_db(s3, db_filepath)
    transcript = call_transcription_api(audio_filepath)
    analysis = analyze_transcript(audio_filepath, transcript)
    save_to_database(conn, db_filepath, audio_filepath, transcript, analysis)

def lambda_handler(event, context):
    download_path = r'tmp/audio.mp3'
    db_filepath = r"users/user_test/transcriptions.db"
    file_download(event, download_path)
    start_process(download_path, db_filepath)
    return {
        "statusCode": 200, 
        "body": "Process completed successfully"
    }

if __name__ == "__main__":
    audio_filepath = r"data/recording_04042024151458.mp3"
    db_filepath = r"data/transcriptions.db"
    start_process(audio_filepath, db_filepath)