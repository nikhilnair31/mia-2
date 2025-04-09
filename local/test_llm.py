import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Keys
GEMINI_API_KEY = os.environ.get("GOOGLE_API")
if not GEMINI_API_KEY:
    raise ValueError("GOOGLE_API environment variable not set.")

# Vars
MODEL_ID = "gemini-2.0-flash"
LLM_API_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent?key={GEMINI_API_KEY}"

# Functions
def call_llm_api(sysprompt, userprompt):
    print(f"\nLLM...")

    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": userprompt}
                ]
            }
        ],
        "systemInstruction": {
            "parts": [
                {"text": sysprompt}
            ]
        },
        "generationConfig": {
            "responseMimeType": "text/plain"
        }
    }

    response = requests.post(LLM_API_ENDPOINT, headers=headers, json=data)
    return response.json()