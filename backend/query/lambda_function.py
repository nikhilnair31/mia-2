import os
import json
import boto3
import logging
import sqlite3
import traceback
from db import (
    query_screenshots_tbl
)
from file import (
    check_s3_object_exists, 
    file_download
)

logger = logging.getLogger()
logger.setLevel("INFO")

s3 = boto3.client('s3')

BUCKET_NAME = "mia-2"
DB_TEMP_FILEPATH = f"/tmp/screenshots.db"

def lambda_handler(event, context):
    logger.info(f"Event: {json.dumps(event)}")
    
    try:
        body = event.get('body')
        if isinstance(body, str):
            body = json.loads(body)
        
        username = body.get('username')
        query_text = body.get('content')
        logger.info(f"username: {username} | query_text: {query_text}")
        
        if not username or not query_text:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameters'
                })
            }
        
        # Download db file from S3
        db_object_key = f'data/{username}/user_data.db'
        db_exists = check_s3_object_exists(s3, BUCKET_NAME, db_object_key)
        if db_exists:
            db_download_success = file_download(s3, BUCKET_NAME, db_object_key, DB_TEMP_FILEPATH)
            if not db_download_success:
                raise Exception(f"Failed to download database file from S3: {BUCKET_NAME}/{db_object_key}")
        else:
            db_init_success = initialize_screenshots_tbl(DB_TEMP_FILEPATH)
            if not db_init_success:
                raise Exception(f"Failed to initialize new database at {DB_TEMP_FILEPATH}")

        # Get results from querying DB
        results = query_screenshots_tbl(DB_TEMP_FILEPATH, query_text)
        logger.info(f"results: {results}")
        
        # Cleanup temp file
        os.unlink(local_db_path)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(results)
        }
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error in lambda_handler: {str(e)}\nStacktrace:\n{error_traceback}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "stacktrace": error_traceback
            })
        }