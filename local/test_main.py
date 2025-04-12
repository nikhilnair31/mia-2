import os
import json
import boto3
import logging
import traceback
from test_logic import analyze_transcript
from test_stt import call_transcription_api
from test_audio import preprocess_ambient_audio
from test_db import initialize_db, save_to_database
from test_file import check_s3_object_exists, get_s3_file_metadata, file_download, file_upload

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

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

def start_process(audio_objectkey, audio_filepath, db_filepath):
    print(f"Starting process with audio: {audio_filepath} and DB: {db_filepath}")
    
    db_success = initialize_db(db_filepath)
    if not db_success:
        raise Exception(f"Failed to initialize database at {db_filepath}")
    
    transcript_json = call_transcription_api(audio_filepath)
    if not transcript_json:
        raise Exception("Transcription failed")
    
    analysis_json = analyze_transcript(audio_filepath, transcript_json)
    if not analysis_json:
        raise Exception("Analysis failed")
    
    transcript_data = json.dumps(transcript_json)
    transcript_text = transcript_json.get("text", "")
    analysis_data = json.dumps(analysis_json)
    
    save_success = save_to_database(db_filepath, audio_objectkey, transcript_data, transcript_text, analysis_data)
    if not save_success:
        raise Exception("Failed to save to database")
    
    print("Process completed successfully")
    return True

def lambda_handler(event, context):
    print(f"Event: {event}")
    
    try:
        db_name = "data.db"
        audio_temp_filepath = f"/tmp/temp_audio_file.mp3"
        db_temp_filepath = f"/tmp/transcriptions.db"
        
        # Get bucket details and audio file metadata
        bucket_name, audio_object_key = get_s3_details(event)
        audio_metadata = get_s3_file_metadata(s3, bucket_name, audio_object_key)
        print(f"Audio Metadata: {audio_metadata}")
        
        # Download audio file from S3
        audio_download_success = file_download(s3, bucket_name, audio_object_key, audio_temp_filepath)
        if not audio_download_success:
            raise Exception(f"Failed to download audio file from S3: {bucket_name}/{audio_object_key}")

        # Check by metadata if can be processed
        processed_audio_temp_filepath = audio_temp_filepath
        if audio_metadata.get('preprocessaudiofile') == 'true':
            processed_audio_temp_filepath = preprocess_ambient_audio(audio_temp_filepath)
        
        # Download db file from S3
        user_name = audio_object_key.split('/')[0] if '/' in audio_object_key else ''
        db_object_key = f'{user_name}/data/{db_name}'
        db_exists = check_s3_object_exists(s3, bucket_name, db_object_key)
        if db_exists:
            db_download_success = file_download(s3, bucket_name, db_object_key, db_temp_filepath)
            if not db_download_success:
                raise Exception(f"Failed to download database file from S3: {bucket_name}/{db_object_key}")
        else:
            db_init_success = initialize_db(db_temp_filepath)
            if not db_init_success:
                raise Exception(f"Failed to initialize new database at {db_temp_filepath}")
        
        # Process audio
        start_process(audio_object_key, processed_audio_temp_filepath, db_temp_filepath)
        
        # Upload db to S3
        db_upload_success = file_upload(s3, bucket_name, db_object_key, db_temp_filepath)
        if not db_upload_success:
            raise Exception(f"Failed to upload database file from S3: {bucket_name}/{db_object_key}")
        
        # Delete audio in s3
        if audio_metadata.get('saveaudiofile') == 'false':
            audio_delete_success = s3.delete_object(Bucket=bucket_name, Key=audio_object_key)
            if not audio_delete_success:
                raise Exception(f"Failed to delete audio file from S3: {bucket_name}/{audio_object_key}")
        
        return {
            "statusCode": 200, 
            "body": "Process completed successfully"
        }
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Error in lambda_handler: {str(e)}\nStacktrace:\n{error_traceback}")
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}\nStacktrace:\n{error_traceback}"
        }