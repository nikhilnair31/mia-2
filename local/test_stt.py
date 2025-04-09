import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Keys
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set.")

# Vars
STT_API_ENDPOINT = "https://api.groq.com/v1/chat/completions"
STT_MODEL = "gpt-4-turbo"

# Functions
def call_transcription_api(temp_file):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    
    with open(temp_file, 'rb') as file_data:
        files = {
            'file': (os.path.basename(temp_file), file_data),
        }
        
        data = {
            'model': STT_MODEL,
            'response_format': 'verbose_json'
        }
        
        response = requests.post(STT_API_ENDPOINT, headers=headers, files=files, data=data)
    
    transcription_result = response.json()
    
    full_text = transcription_result.get('text', '')

    return full_text