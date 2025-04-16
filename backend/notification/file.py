import os

def check_s3_object_exists(s3, bucket_name, object_key):
    try:
        s3.head_object(Bucket=bucket_name, Key=object_key)
        print(f"Object exists: {bucket_name}/{object_key}")
        return True
    except Exception as e:
        print(f"Object does not exist or error: {bucket_name}/{object_key} - {e}")
        return False

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
    print(f"Uploading from {local_filepath} to {bucket_name}/{object_key}")
    
    try:
        if os.path.exists(local_filepath):
            s3.upload_file(local_filepath, bucket_name, object_key)
            print(f"Uploaded database to {bucket_name}/{object_key}")
        
        s3.download_file(bucket_name, object_key, local_filepath)
        print(f"Upload successful!")
        return True
    except Exception as e:
        print(f"Upload error: {e}")
        return False

def get_all_users(s3, bucket_name):
    result = s3.list_objects_v2(
        Bucket=bucket_name,
        Prefix='data/',
        Delimiter='/'
    )
    
    users = []
    if 'CommonPrefixes' in result:
        for prefix in result['CommonPrefixes']:
            # Extract just the username from the prefix
            username = prefix['Prefix'].split('/')[-2]  # Get the part before the last slash
            users.append(username)
    print(f"users: {users}")
    
    return users