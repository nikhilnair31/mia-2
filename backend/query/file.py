import os
import logging
import tempfile

logger = logging.getLogger()
logger.setLevel("INFO")

def check_s3_object_exists(s3, bucket_name, object_key):
    try:
        s3.head_object(Bucket=bucket_name, Key=object_key)
        logger.info(f"Object exists: {bucket_name}/{object_key}")
        return True
    except Exception as e:
        logger.error(f"Object does not exist or error: {bucket_name}/{object_key} - {e}")
        return False

def file_download(s3, bucket_name, object_key, local_filepath):
    logger.info(f"Downloading from Bucket: {bucket_name}, Key: {object_key}")
    logger.info(f"Saving to: {local_filepath}")

    try:
        os.makedirs(os.path.dirname(local_filepath), exist_ok=True)

        s3.download_file(bucket_name, object_key, local_filepath)
        logger.info(f"Download successful!")
        return True
    except Exception as e:
        logger.error(f"Download error: {e}")
        return False

def generate_presigned_url(s3, bucket_name, object_key: str) -> str:
    try:
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_key
            },
            ExpiresIn=180
        )
        return presigned_url
    except Exception as e:
        logger.error(f"Error generating presigned URL for {object_key}: {str(e)}")
        return ""