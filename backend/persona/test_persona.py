import os
import json
import boto3
import logging
import traceback
from test_llm import call_llm_api
from test_file import check_s3_object_exists, file_download, file_upload, get_all_users
from test_db import initialize_personas_db, get_recent_transcripts, save_persona_to_db

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
PERSONA_PROMPT = """
You are analyzing a series of transcribed conversations to create a persona profile.
Based on the following transcripts, create a detailed persona that includes:
1. Primary personality traits and communication style
2. Interests, topics, and subjects frequently discussed
3. Social patterns (who they talk to, how they interact)
4. Emotional patterns and tendencies
5. Any recurring themes or topics

Format your response as JSON with these fields:
{
    "personality_traits": [],
    "communication_style": "",
    "interests": [],
    "social_patterns": "",
    "emotional_tendencies": "",
    "recurring_themes": []
}

Keep your analysis balanced, neutral, and focused only on what's evident in the data.
"""

def generate_persona(username, transcripts):
    if not transcripts:
        return None
    
    user_prompt = f"User: {username}\n\nTranscripts:\n"
    for i, transcript in enumerate(transcripts, 1):
        user_prompt += f"\n--- Transcript {i} ---\n{transcript}\n"
    
    try:
        response = call_llm_api(PERSONA_PROMPT, user_prompt)
        
        if isinstance(response, dict) and 'text' in response:
            persona_text = response['text']
        elif isinstance(response, str):
            persona_text = response
        else:
            persona_text = json.dumps(response)
        # print(f"Persona text: {persona_text}")
        
        try:
            start_idx = persona_text.find('{')
            end_idx = persona_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = persona_text[start_idx:end_idx]
                persona_json = json.loads(json_str)
                # print(f"Persona JSON: {persona_json}")
                return persona_json
            else:
                logger.warning(f"No JSON object found in response for user {username}")
                return {"raw_response": persona_text}
                
        except json.JSONDecodeError:
            logger.warning(f"Could not parse JSON from response for user {username}")
            return {"raw_response": persona_text}
            
    except Exception as e:
        logger.error(f"Error calling LLM API for user {username}: {str(e)}")
        return None

def lambda_handler(event, context):
    print(f"Event: {json.dumps(event)}")
    
    try:
        bucket_name = 'mia-2'
        db_object_key = "personas/personas.db"
        db_temp_filepath = f"/tmp/personas.db"
        
        # Download personas database file from S3
        db_exists = check_s3_object_exists(s3, bucket_name, db_object_key)
        if db_exists:
            db_download_success = file_download(s3, bucket_name, db_object_key, db_temp_filepath)
            if not db_download_success:
                raise Exception(f"Failed to download database file from S3: {bucket_name}/{db_object_key}")
        else:
            db_init_success = initialize_personas_db(db_temp_filepath)
            if not db_init_success:
                raise Exception(f"Failed to initialize new database at {db_temp_filepath}")
        
        users = get_all_users(s3, bucket_name)
        for username in users:
            user_db_temp_filepath = f"/tmp/{username}_data.db"
            user_db_object_key = f"data/{username}/data/data.db"
            user_db_exists = check_s3_object_exists(s3, bucket_name, user_db_object_key)
            if user_db_exists:
                user_db_download_success = file_download(s3, bucket_name, user_db_object_key, user_db_temp_filepath)
                if not user_db_download_success:
                    raise Exception(f"Failed to download database file from S3: {bucket_name}/{user_db_object_key}")
            
            transcripts = get_recent_transcripts(username, user_db_temp_filepath)
            
            if not transcripts:
                print(f"No valid transcripts found for user: {username}")
                continue
            
            persona = generate_persona(username, transcripts)
            if persona:
                save_persona_to_db(db_temp_filepath, username, persona)
        
        # Upload db to S3
        db_upload_success = file_upload(s3, bucket_name, db_object_key, db_temp_filepath)
        if not db_upload_success:
            raise Exception(f"Failed to upload database file from S3: {bucket_name}/{db_object_key}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Persona generation completed successfully",
                "usersProcessed": len(users)
            })
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