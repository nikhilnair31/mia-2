import os

def get_s3_file_metadata(s3, bucket_name, object_key):
    print(f"Fetching metadata for S3 object: {bucket_name}/{object_key}")
    
    try:
        response = s3.head_object(Bucket=bucket_name, Key=object_key)
        
        user_metadata = response.get('Metadata', {})

        metadata = {
            'content_type': response.get('ContentType', '')
        }

        user_metadata = response.get('Metadata', {})
        metadata.update(user_metadata)

        logger.info(f"Successfully retrieved metadata for: {bucket_name}/{object_key}")
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
def file_upload(s3, bucket_name, object_key, local_filepath, metadata):
    print(f"Uploading from {local_filepath} to {bucket_name}/{object_key}")
    
    try:
        if os.path.exists(local_filepath):
            extra_args = {}
            extra_args['Metadata'] = metadata
            s3.upload_file(local_filepath, bucket_name, object_key, ExtraArgs=extra_args)
            print(f"Uploaded database to {bucket_name}/{object_key}")
        
        s3.download_file(bucket_name, object_key, local_filepath)
        print(f"Upload successful!")
        return True
    except Exception as e:
        print(f"Upload error: {e}")
        return False