import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Keys
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set.")

# Vars
STT_MODEL = "whisper-large-v3-turbo"
STT_API_ENDPOINT = "https://api.groq.com/openai/v1/audio/transcriptions"

# Functions
def call_transcription_api(temp_file_path):
    print(f"Transcribing...")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    
    with open(temp_file_path, 'rb') as file_data:
        files = {
            'file': (os.path.basename(temp_file_path), file_data),
        }
        
        data = {
            'model': STT_MODEL,
            'response_format': 'verbose_json'
        }
        
        response = requests.post(STT_API_ENDPOINT, headers=headers, files=files, data=data)
        print(f"Response status code: {response}")
    
    transcription_result = response.json()
    full_text = transcription_result.get('text', '')

    return full_text