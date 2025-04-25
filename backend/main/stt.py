import os
import json
import logging
import requests

logger = logging.getLogger()
logger.setLevel("INFO")

PROVIDER = "groq"

def call_transcription_api(temp_file_path):
    logger.info(f"\nTranscribing...")

    if PROVIDER == "groq":
        response_json = call_groq_whisper(temp_file_path)
        return format_groq_response(response_json)
    
    return "", {}
    
def call_groq_whisper(temp_file_path):
    logger.info(f"\nUsing Groq Whisper...")

    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable not set.")
        
    STT_MODEL = "whisper-large-v3-turbo"
    STT_API_ENDPOINT = "https://api.groq.com/openai/v1/audio/transcriptions"

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
    
    response_json = response.json()
    logger.info(f"response_json: {response_json}")

    return response_json
def format_groq_response(response_json):
    THRESHOLDS = {
        'speech_confidence': 0.3,
        'language_model_confidence': -1,
        'compression_quality': 0.35,
        'min_duration': 0.3,
    }

    formatted_segments = []
    segments_list = response_json.get('segments', [])
    for segment in segments_list:
        start_time = segment.get('start', 0)
        end_time = segment.get('end', 0)
        text = segment.get('text', '').strip()
        
        segment_duration = end_time - start_time
        if segment_duration < THRESHOLDS['min_duration']:
            continue
            
        no_speech_prob = segment.get('no_speech_prob', 0)
        speech_confidence = 1 - no_speech_prob
        
        avg_logprob = segment.get('avg_logprob', -1)
        
        compression_ratio = segment.get('compression_ratio', 0)
        
        if (speech_confidence >= THRESHOLDS['speech_confidence'] and
            avg_logprob >= THRESHOLDS['language_model_confidence'] and
            compression_ratio >= THRESHOLDS['compression_quality']):
            
            timestamp = f"[{start_time:.2f}:{end_time:.2f}]"
            
            formatted_segments.append(f"{timestamp} - {text}\n")
    
    formatted_text = "\n".join(formatted_segments)

    raw_text = response_json.get('text', '').strip()

    return json.dumps(response_json), raw_text, formatted_text