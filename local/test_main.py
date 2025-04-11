import os
import boto3
import logging
from test_db import initialize_db, save_to_database
from test_logic import analyze_transcript
from test_stt import call_transcription_api

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def file_download(bucket_name, object_key, local_filepath):
    print(f"Downloading from Bucket: {bucket_name}, Key: {object_key}")
    print(f"Saving to: {local_filepath}")
    
    try:
        os.makedirs(os.path.dirname(local_filepath), exist_ok=True)
        
        s3.download_file(bucket_name, object_key, local_filepath)
        print(f"Download successful!")
        return True
    except Exception as e:
        print(f"Download error: {e}")
        return False
def file_upload(bucket_name, object_key, local_filepath):
    print(f"Uploading from {local_filepath} to Bucket: {bucket_name}, Key: {object_key}")
    
    try:
        if os.path.exists(local_filepath):
            s3.upload_file(local_filepath, bucket_name, object_key)
            print(f"Uploaded database to S3: {bucket_name}/transcriptions.db")
        
        s3.download_file(bucket_name, object_key, local_filepath)
        print(f"Upload successful!")
        return True
    except Exception as e:
        print(f"Upload error: {e}")
        return False

def get_s3_details(event):
    try:
        record = event['Records'][0]
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        
        if not bucket_name or not object_key:
            raise ValueError("Could not determine bucket name or object key from the event")
            
        print(f"Detected S3 object - Bucket: {bucket_name}, Key: {object_key}")
        return bucket_name, object_key
    except (KeyError, IndexError) as e:
        print(f"Error extracting S3 details: {e}")
        raise

def start_process(audio_filepath, db_filepath):
    print(f"Starting process with audio: {audio_filepath} and DB: {db_filepath}")
    
    db_success = initialize_db(db_filepath)
    if not db_success:
        raise Exception(f"Failed to initialize database at {db_filepath}")
    
    transcript_text = call_transcription_api(audio_filepath)
    if not transcript_text:
        raise Exception("Transcription failed")
    
    analysis = analyze_transcript(audio_filepath, transcript_text)
    
    save_success = save_to_database(db_filepath, audio_filepath, transcript_text, analysis)
    if not save_success:
        raise Exception("Failed to save to database")
    
    print("Process completed successfully")
    return True

def lambda_handler(event, context):
    print(f"Lambda handler started")
    print(f"Event: {event}")
    
    try:
        db_object_key = "transcriptions.db"
        audio_temp_filepath = f"/tmp/temp_audio_file.mp3"
        db_temp_filepath = f"/tmp/transcriptions.db"
        
        bucket_name, audio_object_key = get_s3_details(event)
        
        audio_download_success = file_download(bucket_name, audio_object_key, audio_temp_filepath)
        if not audio_download_success:
            raise Exception(f"Failed to download audio file from S3: {bucket_name}/{audio_object_key}")
        db_download_success = file_download(bucket_name, db_object_key, db_temp_filepath)
        if not db_download_success:
            raise Exception(f"Failed to download database file from S3: {bucket_name}/{db_object_key}")
        
        start_process(audio_temp_filepath, db_temp_filepath)
        
        db_upload_success = file_upload(bucket_name, db_object_key, db_temp_filepath)
        if not db_upload_success:
            raise Exception(f"Failed to upload database file from S3: {bucket_name}/{db_object_key}")
        
        return {
            "statusCode": 200, 
            "body": "Process completed successfully"
        }
        
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }

if __name__ == "__main__":
    audio_filepath = "data/recording_04042024151458.mp3"
    db_filepath = "data/transcriptions.db"
    start_process(audio_filepath, db_filepath)