import os

def check_s3_object_exists(s3, bucket_name, object_key):
    try:
        s3.head_object(Bucket=bucket_name, Key=object_key)
        print(f"Object exists: {bucket_name}/{object_key}")
        return True
    except Exception as e:
        print(f"Object does not exist or error: {bucket_name}/{object_key} - {e}")
        return False

def get_s3_file_metadata(s3, bucket_name, object_key):
    print(f"Fetching metadata for S3 object: {bucket_name}/{object_key}")
    
    try:
        response = s3.head_object(Bucket=bucket_name, Key=object_key)
        
        user_metadata = response.get('Metadata', {})
        
        metadata = {
            'content_type': response.get('ContentType', ''),
            'battery_level': user_metadata.get('batterylevel'),
            'timestamp': user_metadata.get('currenttimeformattedstring'),
            'filename': user_metadata.get('filename'),
            'latitude': user_metadata.get('latitude'),
            'longitude': user_metadata.get('longitude'),
            'movement_status': user_metadata.get('movementstatus'),
            'preprocessaudiofile': user_metadata.get('preprocessaudiofile'),
            'saveaudiofile': user_metadata.get('saveaudiofile'),
            'source': user_metadata.get('source'),
            'username': user_metadata.get('username')
        }
        
        print(f"Successfully retrieved metadata for: {bucket_name}/{object_key}")
        return metadata
        
    except Exception as e:
        print(f"Error retrieving metadata: {e}")
        return None

def file_download(s3, bucket_name, object_key, local_filepath):
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
def file_upload(s3, bucket_name, object_key, local_filepath):
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