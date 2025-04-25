import os
import json
import boto3
import logging
import datetime
import traceback
from llm import (
    call_llm_api
)
from file import (
    check_s3_object_exists, 
    file_download, file_upload, 
    get_all_users
)
from db import (
    initialize_personas_tbl, 
    insert_persona_to_tbl, 
    get_recent_transcripts, get_latest_persona
)

logger = logging.getLogger()
logger.setLevel("INFO")

s3 = boto3.client('s3')

BUCKET_NAME = 'mia-2'

def generate_persona(username, transcript_data, latest_persona_str, timestamp_str) -> str:
    PERSONA_SYSTEM_PROMPT = """
        You are an AI assistant tasked with analyzing transcribed conversations to create and update persona profiles. Your goal is to provide a clear, concise, and accurate representation of the main subject's personality and behavior based on the available data.

        You'll recieve information in the following format:

        <todays_date>
        {{TODAYS_DATE}}
        </todays_date>

        <user_persona>
        {{USER_PERSONA}}
        </user_persona>

        <reccent_transcripts>
        {{RECENT_TRANSCRIPTS}}
        </reccent_transcripts>

        Instructions:
        1. Carefully read through the transcripts.
        2. Determine if there are multiple speakers in the transcripts. If so, identify the main subject of the persona profile.
        3. Compare the new information with the latest persona profile.
        4. Update the persona profile based on the new information, focusing on the following aspects:
        a. Primary personality traits and communication style
        b. Interests, topics, and subjects frequently discussed
        c. Social patterns (who they talk to, how they interact)
        d. Emotional patterns and tendencies
        e. Any recurring themes or topics

        5. Before generating the final output, wrap your reasoning process for each aspect of the persona profile in <persona_analysis> tags. For each aspect:
        a. List key quotes from the transcripts that relate to this aspect.
        b. Compare these quotes to the existing profile, noting confirmations, contradictions, or new information.
        c. Summarize the changes or updates needed for this aspect.
        It's OK for this section to be quite long.

        6. Generate a JSON output with the updated persona profile, using the following structure:
        {
            "personality_traits": [],
            "communication_style": "",
            "interests": [],
            "social_patterns": "",
            "emotional_tendencies": "",
            "recurring_themes": []
        }

        Important guidelines:
        - Keep your analysis balanced, neutral, and focused only on what's evident in the data.
        - Be aware that the transcripts may include conversations from movies, TV shows, or other people. Focus on identifying and analyzing the main subject's characteristics.
        - Build upon the most recent persona profile, making adjustments based on the newer transcripts.
        - If there's insufficient information to update a particular aspect, maintain the previous information for that field.

        Please proceed with your analysis and updated persona profile.
    """
    USER_PROMPT = """
        <todays_date>
        {{TODAYS_DATE}}
        </todays_date>

        <user_persona>
        {{USER_PERSONA}}
        </user_persona>

        <reccent_transcripts>
        {{RECENT_TRANSCRIPTS}}
        </reccent_transcripts>
    """
    
    transcript_prompt = "\n".join([f"\n--- Transcript {row[0]} ---\n{row[1]}" for i, row in enumerate(transcript_data, 1)])

    USER_PROMPT = USER_PROMPT.replace("{{TODAYS_DATE}}", timestamp_str)
    USER_PROMPT = USER_PROMPT.replace("{{USER_PERSONA}}", latest_persona_str)
    USER_PROMPT = USER_PROMPT.replace("{{RECENT_TRANSCRIPTS}}", transcript_prompt)
    logger.info(f'USER_PROMPT:\n{USER_PROMPT[:100]}')
    
    try:
        response = call_llm_api(PERSONA_SYSTEM_PROMPT, USER_PROMPT)
        
        response_text = response['candidates'][0]['content']['parts'][0]['text']

        return response_text
            
    except Exception as e:
        logger.error(f"Error calling LLM API for user {username}: {str(e)}")
        return None

def lambda_handler(event, context):
    logger.info(f"Event: {json.dumps(event)}")
    
    try:
        users = get_all_users(s3, BUCKET_NAME)
        for username in users:
            user_db_temp_filepath = f"/tmp/{username}_data.db"
            user_db_object_key = f"data/{username}/user_data.db"

            # Check if user's db exists
            user_db_exists = check_s3_object_exists(s3, BUCKET_NAME, user_db_object_key)
            if user_db_exists:
                user_db_download_success = file_download(s3, BUCKET_NAME, user_db_object_key, user_db_temp_filepath)
                if not user_db_download_success:
                    raise Exception(f"Failed to download database file from S3: {BUCKET_NAME}/{user_db_object_key}")
            
            # Date vars
            timestamp_str = str(datetime.datetime.now())

            # Get user's recent transcripts
            transcript_data = get_recent_transcripts(user_db_temp_filepath)
            # Get user's latest persona
            latest_persona_str = get_latest_persona(user_db_temp_filepath)
            
            # Generate person based transcriptions
            new_persona_str = generate_persona(username, transcript_data, latest_persona_str, timestamp_str)
            
            # Ensure the personas table exists
            initialize_personas_tbl(user_db_temp_filepath)
            # Then insert into DB table
            insert_data = (
                username,
                new_persona_str,
                timestamp_str
            )
            insert_persona_to_tbl(user_db_temp_filepath, insert_data)
        
            # Upload to S3
            db_upload_success = file_upload(s3, BUCKET_NAME, user_db_object_key, user_db_temp_filepath)
            if not db_upload_success:
                raise Exception(f"Failed to upload database file from S3: {BUCKET_NAME}/{user_db_object_key}")
        
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