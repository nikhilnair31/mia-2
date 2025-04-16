import os
import json
import boto3
import datetime
import traceback
from llm import call_llm_api
from file import check_s3_object_exists, file_download, file_upload, get_all_users
from db import initialize_personas_tbl, get_recent_transcripts, insert_persona_to_tbl

s3 = boto3.client('s3')

bucket_name = 'mia-2'

PERSONA_PROMPT = """
    You are analyzing a series of transcribed conversations to create a persona profile.
    Based on the following transcripts, create a detailed persona that includes:
    1. Primary personality traits and communication style
    2. Interests, topics, and subjects frequently discussed
    3. Social patterns (who they talk to, how they interact)
    4. Emotional patterns and tendencies
    5. Any recurring themes or topics

    Format your response as JSON with these fields: {
        "personality_traits": [],
        "communication_style": "",
        "interests": [],
        "social_patterns": "",
        "emotional_tendencies": "",
        "recurring_themes": []
    }

    Keep your analysis balanced, neutral, and focused only on what's evident in the data.
"""

def generate_persona(username, transcripts) -> str:
    user_prompt = f"User: {username}\n\nTranscripts:\n"
    for i, transcript in enumerate(transcripts, 1):
        user_prompt += f"\n--- Transcript {i} ---\n{transcript}\n"
    
    try:
        response = call_llm_api(PERSONA_PROMPT, user_prompt)
        
        if isinstance(response, dict) and "text" in response:
            return response["text"]
        elif hasattr(response, "json"):
            return response.json().get("text", "-")
        else:
            return "-"
            
    except Exception as e:
        print(f"Error calling LLM API for user {username}: {str(e)}")
        return None

def lambda_handler(event, context):
    print(f"Event: {json.dumps(event)}")
    
    try:
        users = get_all_users(s3, bucket_name)
        for username in users:
            user_db_temp_filepath = f"/tmp/{username}_data.db"
            user_db_object_key = f"data/{username}/user_data.db"

            # Check if user's db exists
            user_db_exists = check_s3_object_exists(s3, bucket_name, user_db_object_key)
            if user_db_exists:
                user_db_download_success = file_download(s3, bucket_name, user_db_object_key, user_db_temp_filepath)
                if not user_db_download_success:
                    raise Exception(f"Failed to download database file from S3: {bucket_name}/{user_db_object_key}")
            
            # Get user's recent transcripts
            transcripts = get_recent_transcripts(user_db_temp_filepath)
            if not transcripts:
                print(f"No valid transcripts found for user: {username}")
                continue
            
            # Generate person based transcriptions
            persona_str = generate_persona(username, transcripts)
            
            # Date vars
            today_date = datetime.datetime.now()
            today_str = str(today_date.strftime('%Y-%m-%d'))
            # print(f"today_str: {today_str}")
            timestamp_str = str(datetime.datetime.now())
            # print(f"timestamp_str: {timestamp_str}")
            
            # Ensure the personas table exists
            initialize_personas_tbl(user_db_temp_filepath)
            # Then insert into DB table
            insert_data = (
                username,
                persona_str,
                today_str,
                timestamp_str
            )
            insert_persona_to_tbl(user_db_temp_filepath, insert_data)
        
            # Upload to S3
            db_upload_success = file_upload(s3, bucket_name, user_db_object_key, user_db_temp_filepath)
            if not db_upload_success:
                raise Exception(f"Failed to upload database file from S3: {bucket_name}/{user_db_object_key}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Persona generation completed successfully",
                "usersProcessed": len(users)
            })
        }
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Error in lambda_handler: {str(e)}\nStacktrace:\n{error_traceback}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "stacktrace": error_traceback
            })
        }