import json
import boto3
import random
import datetime
import traceback
from llm import call_llm_api
from file import check_s3_object_exists, file_download
from db import get_recent_transcripts

S3 = boto3.client('s3')

BUCKET_NAME = 'mia-2'

NOTIFICATION_PROMPT = """
You are an AI assistant designed to analyze historical transcripts and create actionable notifications for users. Your task is to review the following transcripts and determine if a notification should be generated based on their content.

Here are the historical transcripts to analyze:

<historical_transcripts>
{{HISTORICAL_TRANSCRIPTS}}
</historical_transcripts>

Please follow these steps to complete the task:

1. Carefully review the provided transcripts.
2. Extract and quote relevant parts of the transcripts.
3. Categorize potential actionable items as events, reminders, or tasks.
4. Evaluate the urgency and importance of each item.
5. Determine if a notification should be generated based on your analysis.
6. If a notification is warranted, create a concise, actionable content of no more than 15 words.

Wrap your analysis inside <transcript_analysis> tags:

<transcript_analysis>
- Quote relevant parts of the transcripts
- Categorize potential actionable items (events, reminders, tasks)
- Evaluate the urgency and importance of each item
- Summarize the key points from the transcripts
- Explain your reasoning for deciding whether a notification is needed
- If applicable, draft the notification content and explain how it relates to the transcripts
</transcript_analysis>

After your analysis, provide your final output in the following format:

is_notification: [true/false]
content: [Your 15-word max actionable content OR "No notification required"]

Remember:
- The content must be directly based on information from the transcripts.
- Keep the content concise and actionable, focusing on events, reminders, or tasks.
- Ensure the content does not exceed 15 words.
- If no notification is needed, set is_notification to false and content to "No notification required".
"""

def generate_notification(username, transcripts) -> dict:
    user_prompt = f"Transcripts:\n"
    for i, transcript in enumerate(transcripts, 1):
        user_prompt += f"\n--- Transcript {i} ---\n{transcript}\n"
    print(f'\nuser_prompt:\n{user_prompt}\n')
    
    try:
        response = call_llm_api(NOTIFICATION_PROMPT, user_prompt)
        response_text = response['candidates'][0]['content']['parts'][0]['text']
        print(f'type: {type(response_text)} | response_text: {response_text}')

        return True, response_text.split('content:')[1].strip()

        # if "true" in response_text.lower().strip():
        #     return True, response_text.split('content:')[1].strip()
        # else:
        #     return False, None
            
    except Exception as e:
        print(f"Error calling LLM API for user {username}: {str(e)}")
        return False, None

def get_notification_data(username):
    user_db_object_key = f"data/{username}/user_data.db"
    user_db_temp_filepath = f"/tmp/{username}_data.db"

    # Check if user's db exists
    user_db_exists = check_s3_object_exists(S3, BUCKET_NAME, user_db_object_key)
    if user_db_exists:
        user_db_download_success = file_download(S3, BUCKET_NAME, user_db_object_key, user_db_temp_filepath)
        if not user_db_download_success:
            raise Exception(f"Failed to download database file from S3: {BUCKET_NAME}/{user_db_object_key}")
            
    # Get user's recent transcripts
    transcripts = get_recent_transcripts(user_db_temp_filepath)
    if not transcripts:
        print(f"No valid transcripts found for user: {username}")
        return
            
    # Generate notification data
    show_notif_bool, notif_content_str = generate_notification(username, transcripts)
    print(f'show_notif_bool: {show_notif_bool} | notif_content_str: {notif_content_str}')

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
    print(f"\nevent: {event}\n")
    
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
            print(f"Received feedback from {username}: {feedback_type}")
            
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
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        
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