import os
import logging
import requests

logger = logging.getLogger()
logger.setLevel("INFO")

PROVIDER = "gemini"

def call_llm_api(sysprompt, userprompt):
    logger.info(f"\nLLM...")

    if PROVIDER == "gemini":
        response_json = call_gemini(sysprompt, userprompt)
        return response_json
        
    return ""

def call_gemini(sysprompt, userprompt):
    logger.info(f"\nCalling Gemini...")

    GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")

    MODEL_ID = "gemini-2.0-flash"
    LLM_API_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent?key={GEMINI_API_KEY}"

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
    response_json = response.json()
    # logger.info(f"response_json: {response_json}")
    
    return response_json