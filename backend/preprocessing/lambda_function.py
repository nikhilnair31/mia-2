import json
import boto3
import traceback
from audio import preprocess_ambient_audio
from file import get_s3_file_metadata, file_download, file_upload

s3 = boto3.client('s3')

def lambda_handler(event, context):
    print(f"Event: {event}")

    bucket_name = 'mia-2'
    audio_temp_filepath = f"/tmp/temp_audio_file.mp3"
    
    try:
        # Get event details
        audio_object_key = event.get('object_key')
        print(f"audio_object_key: {audio_object_key}")
        
        # Get audio file metadata
        audio_metadata = get_s3_file_metadata(s3, bucket_name, audio_object_key)
        audio_metadata['preprocessfile'] = 'false'
        print(f"audio_metadata: {audio_metadata}")

        # Download audio file from S3
        audio_download_success = file_download(s3, bucket_name, audio_object_key, audio_temp_filepath)
        if not audio_download_success:
            raise Exception(f"Failed to download audio file from S3: {bucket_name}/{audio_object_key}")

        # Check by metadata if can be processed
        processed_audio_temp_filepath = preprocess_ambient_audio(audio_temp_filepath)
        
        # Upload audio to S3
        prefix = audio_object_key.split('/')[:-1]
        audio_filename = audio_object_key.split('/')[-1]
        new_audio_filename = f'{audio_filename.split(".")[0]}_processed.m4a'
        audio_processed_object_key = f'{'/'.join(prefix)}/{new_audio_filename}'
        audio_upload_success = file_upload(s3, bucket_name, audio_processed_object_key, audio_temp_filepath, audio_metadata)
        if not audio_upload_success:
            raise Exception(f"Failed to upload database file from S3: {bucket_name}/{audio_processed_object_key}")
        
        # Delete audio in s3
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