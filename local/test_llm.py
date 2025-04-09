import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Keys
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set.")

# Vars
LLM_API_ENDPOINT = "https://api.groq.com/v1/chat/completions"
LLM_MODEL = "gpt-4-turbo"

# Functions
def call_llm_api(sysprompt, userprompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    data = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": sysprompt
            },
            {
                "role": "user",
                "content": userprompt
            }
        ]
    }

    response = requests.post(LLM_API_ENDPOINT, headers=headers, json=data)
    analysis_result = response.json()

    return analysis_result