import json
import boto3
import random
import logging
import datetime
import traceback
from llm import (
    call_llm_api
)
from file import (
    check_s3_object_exists, 
    file_upload, file_download
)
from db import (
    initialize_notifications_tbl, 
    insert_notification_to_tbl, 
    get_recent_transcripts, get_recent_notifications, get_latest_persona
)

logger = logging.getLogger()
logger.setLevel("INFO")

s3 = boto3.client('s3')

BUCKET_NAME = 'mia-2'

def generate_notification(username, transcript_data, notification_data, persona_str, timestamp_str) -> dict:
    NOTIFICATION_SYSTEM_PROMPT = """
        You are an AI assistant designed to analyze historical transcripts and create actionable notifications for users. Your task is to review the provided transcripts and determine if a notification should be generated based on their content.

        You'll recieve information in the following format:
        
        <todays_date>
        {{TODAYS_DATE}}
        </todays_date>

        <user_persona>
        {{USER_PERSONA}}
        </user_persona>

        <recent_notifications>
        {{RECENT_NOTIFICATIONS}}
        </recent_notifications>

        <recent_transcripts>
        {{RECENT_TRANSCRIPTS}}
        </recent_transcripts>

        Please follow these steps to complete the task:

        1. Carefully review the provided transcripts.
        2. Extract relevant quotes from the transcripts.
        3. Categorize potential actionable items as events, reminders, or tasks.
        4. Evaluate the urgency and importance of each item, considering the user's persona and the time relative to the present.
        5. List out potential notifications based on your analysis.
        6. Determine if a notification should be generated based on your analysis.
        7. If a notification is warranted, create a concise, actionable content of no more than 15 words.

        Wrap your analysis inside <detailed_analysis> tags:

        <detailed_analysis>
        - Quote relevant parts of the transcripts
        - Categorize potential actionable items (events, reminders, tasks)
        - Evaluate the urgency and importance of each item, considering the user's persona and time relative to present
        - Summarize the key points from the transcripts
        - List potential notifications (up to 3) based on your analysis
        - For each potential notification, assess its time sensitivity (urgent, soon, or future)
        - Explain your reasoning for deciding whether a notification is needed and which one to choose
        - If applicable, draft the final notification content and explain how it relates to the transcripts
        </detailed_analysis>

        After your analysis, provide your final output in the following format:

        is_notification: [true/false]
        content: [Your 15-word max actionable content OR "No notification required"]

        Remember:
        - The content must be directly based on information from the transcripts.
        - Keep the content concise and actionable, focusing on events, reminders, or tasks.
        - Ensure the content does not exceed 15 words.
        - Do not refer to specific timestamps in the notification content.
        - If no notification is needed, set is_notification to false and content to "No notification required".
        - Prioritize information based on its relevance to the present time and the user's persona.

        Example output (for illustration only):

        <detailed_analysis>
        [Your detailed analysis would go here]
        </detailed_analysis>

        is_notification: true
        content: Remember to schedule car maintenance appointment this week.

        OR

        is_notification: false
        content: No notification required
    """
    BASE_USER_PROMPT = """
        <todays_date>
        {{TODAYS_DATE}}
        </todays_date>

        <user_persona>
        {{USER_PERSONA}}
        </user_persona>

        <recent_notifications>
        {{RECENT_NOTIFICATIONS}}
        </recent_notifications>

        <recent_transcripts>
        {{RECENT_TRANSCRIPTS}}
        </recent_transcripts>
    """

    recent_notifications_str = "\n".join([f"Notification {row[0]}: {row[1]}\n" for i, row in enumerate(notification_data, 1)])
    logger.info(f'recent_notifications_str:\n{recent_notifications_str}')
    recent_transcripts_str = "\n".join([f"\n--- Transcript {row[0]} ---\n{row[1]}" for i, row in enumerate(transcript_data, 1)])
    logger.info(f'recent_transcripts_str:\n{recent_transcripts_str}')
    
    BASE_USER_PROMPT = BASE_USER_PROMPT.replace('{{TODAYS_DATE}}', timestamp_str)
    BASE_USER_PROMPT = BASE_USER_PROMPT.replace('{{USER_PERSONA}}', persona_str)
    BASE_USER_PROMPT = BASE_USER_PROMPT.replace('{{RECENT_NOTIFICATIONS}}', recent_notifications_str)
    BASE_USER_PROMPT = BASE_USER_PROMPT.replace('{{RECENT_TRANSCRIPTS}}', recent_transcripts_str)
    logger.info(f'BASE_USER_PROMPT:\n{BASE_USER_PROMPT}')
    
    try:
        response = call_llm_api(NOTIFICATION_SYSTEM_PROMPT, BASE_USER_PROMPT)
        logger.info(f'response: {response}')
        response_text = response['candidates'][0]['content']['parts'][0]['text']
        logger.info(f'response_text: {response_text}')
        final_text = response_text.split('</detailed_analysis>')[-1]
        logger.info(f'final_text: {final_text}')
        content_part = final_text.split('content:')[1].strip() if 'content:' in final_text else None
        logger.info(f'content_part: {content_part}')

        if "true" in final_text.lower().strip():
            return True, content_part
        else:
            return False, None
            
    except Exception as e:
        logger.error(f"Error calling LLM API for user {username}: {str(e)}")
        return False, None

def get_notification_data(username):
    user_db_object_key = f"data/{username}/user_data.db"
    user_db_temp_filepath = f"/tmp/{username}_data.db"

    # Check if user's db exists
    user_db_exists = check_s3_object_exists(s3, BUCKET_NAME, user_db_object_key)
    if user_db_exists:
        user_db_download_success = file_download(s3, BUCKET_NAME, user_db_object_key, user_db_temp_filepath)
        if not user_db_download_success:
            raise Exception(f"Failed to download database file from s3: {BUCKET_NAME}/{user_db_object_key}")
    
    # Date vars
    today_date = datetime.datetime.now()
    timestamp_str = str(datetime.datetime.now())

    # Get user's recent notifications
    notification_data = get_recent_notifications(user_db_temp_filepath)
    # Get user's recent transcripts
    transcript_data = get_recent_transcripts(user_db_temp_filepath)
    # Get user's latest persona
    persona_str = get_latest_persona(user_db_temp_filepath)
            
    # Generate notification data
    show_notif_bool, notif_content_str = generate_notification(
        username, transcript_data, notification_data, persona_str, timestamp_str
    )
 
    # Ensure the notifications table exists
    initialize_notifications_tbl(user_db_temp_filepath)
    # Then insert into table
    insert_data = (
        show_notif_bool,
        notif_content_str,
        timestamp_str
    )
    insert_notification_to_tbl(user_db_temp_filepath, insert_data)
        
    # Upload to S3
    db_upload_success = file_upload(s3, BUCKET_NAME, user_db_object_key, user_db_temp_filepath)
    if not db_upload_success:
        raise Exception(f"Failed to upload database file from S3: {BUCKET_NAME}/{user_db_object_key}")

    if show_notif_bool:
        return {
            'notification_to_show': True,
            'notification_content': notif_content_str,
            'notification_id': random.randint(1, 1000000)
        }
    else:
        return {
            'notification_to_show': False,
            'notification_content': None,
            'notification_id': -1
        }

def lambda_handler(event, context):
    logger.info(f"\nevent: {event}\n")
    
    try:
        body = json.loads(event.get('body'))
        # body = event.get('body')
        
        action = body.get('action')
        username = body.get('username', 'User')
        
        if action == 'get_notification':
            notification_data = get_notification_data(username)

            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(notification_data)
            }

        elif action == 'feedback':
            feedback_type = body.get('feedback')
            logger.info(f"Received feedback from {username}: {feedback_type}")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': f"Feedback '{feedback_type}' received. Thanks, {username}!"
                })
            }
    
    except Exception as e:
        logger.error(f"Error: {str(e)}\n{traceback.format_exc()}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'notification_to_show': False,
                'notification_content': '',
                'notification_id': 0
            })
        }