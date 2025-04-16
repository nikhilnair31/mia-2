import os
import json
import time
import boto3
import datetime
import traceback
from logic import analyze_transcript
from stt import call_transcription_api
from db import initialize_db, insert_to_database
from file import check_s3_object_exists, get_s3_file_metadata, file_download, file_upload

lambda_client = boto3.client('lambda')
s3 = boto3.client('s3')

def start_process(audio_objectkey, audio_filepath, db_filepath):
    print(f"Starting process with audio: {audio_filepath} and DB: {db_filepath}")
    
    db_success = initialize_db(db_filepath)
    if not db_success:
        raise Exception(f"Failed to initialize database at {db_filepath}")
    
    transcript_raw_json_str, transcript_raw_text, transcript_processed_text  = call_transcription_api(audio_filepath)
    if not transcript_raw_json_str:
        raise Exception("Transcription failed")
    # print(f"transcript_raw_json_str: {transcript_raw_json_str}\ntranscript_raw_text: {transcript_raw_text}\ntranscript_processed_text: {transcript_processed_text}")
    
    analysis_json_str = analyze_transcript(audio_filepath, transcript_processed_text)
    if not analysis_json_str:
        raise Exception("Analysis failed")
    # print(f"analysis_json_str: {analysis_json_str}")
        
    today_date = datetime.datetime.now()
    today_str = str(today_date.strftime('%Y-%m-%d'))
    # print(f"today_str: {today_str}")
    timestamp_str = str(datetime.datetime.now())
    # print(f"timestamp_str: {timestamp_str}")
    
    insert_data = (
        audio_objectkey,
        transcript_raw_json_str,
        transcript_raw_text,
        transcript_processed_text,
        analysis_json_str,
        today_str,
        timestamp_str
    )
    # print(f"insert_data: {insert_data}")
    insert_success = insert_to_database(db_filepath, insert_data)
    if not insert_success:
        raise Exception("Failed to insert to database")
    
    print("Process completed successfully")
    return True

def lambda_handler(event, context):
    print(f"Event: {event}")

    bucket_name = 'mia-2'
    audio_temp_filepath = f"/tmp/temp_audio_file.mp3"
    db_temp_filepath = f"/tmp/transcriptions.db"
    
    try:
        # Get event details
        record = event['Records'][0]
        audio_object_key = record['s3']['object']['key']
        print(f"audio_object_key: {audio_object_key}")

        # Get audio file metadata
        audio_metadata = get_s3_file_metadata(s3, bucket_name, audio_object_key)
        print(f"audio_metadata: {audio_metadata}")

        if audio_metadata.get('preprocessaudiofile') == 'true':
            # Invoke another Lambda function
            response = lambda_client.invoke(
                FunctionName='mia-2-preprocessing',
                InvocationType='Event',
                Payload=json.dumps({
                    'object_key': audio_object_key
                })
            )
            print(f"Lambda Invoke Response: {response}")

            return {
                "statusCode": 200, 
                "body": "Process completed successfully"
            }
        
        else:
            # Download audio file from S3
            audio_download_success = file_download(s3, bucket_name, audio_object_key, audio_temp_filepath)
            if not audio_download_success:
                raise Exception(f"Failed to download audio file from S3: {bucket_name}/{audio_object_key}")

            # Check by metadata if can be processed
            processed_audio_temp_filepath = audio_temp_filepath
            if audio_metadata.get('preprocessaudiofile') == 'true':
                processed_audio_temp_filepath = preprocess_ambient_audio(audio_temp_filepath)
            
            # Download db file from S3
            user_name = audio_object_key.split('/')[1] if '/' in audio_object_key else ''
            db_object_key = f'data/{user_name}/user_data.db'
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
            save_audio_object_key = audio_object_key if audio_metadata.get('saveaudiofile') == 'true' else '-'
            start_process(save_audio_object_key, processed_audio_temp_filepath, db_temp_filepath)
            
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