import os
import re
from pydub import AudioSegment
from test_llm import call_llm_api

sysprompt = """
Summarize the conversation in a single sentence and classify it as one of the following:
- Monologue: One person speaking with minimal interaction
- Interview: Clear question-answer pattern
- Discussion: Balanced exchange between participants
- Presentation: Informational delivery with some interaction
"""

def analyze_transcript(filepath, transcript):
    audio_len_sec = len_audio(filepath)
    if audio_len_sec < 10:
        return {
            "status": "ignored",
            "reason": "Audio too short",
            "length_seconds": audio_len_sec
        }
    
    classification = get_simple_classification(transcript)
    
    output = {
        "status": "processed",
        "length_seconds": audio_len_sec,
        "classification": classification
    }
    print(f"Analysis result: {output}")
    
    return output
 
def len_audio(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    
    try:
        len = AudioSegment.from_file(file_path).duration_seconds
        print(f"Audio length: {len} seconds")
        return len
    except FileNotFoundError:
        print("Error: FFmpeg not found. Please install FFmpeg and add it to your PATH.")
        raise

def get_basic_speaker_info(transcript):
    speaker_pattern = r'(Speaker \w+|Unknown):\s*'
    speakers = set(re.findall(speaker_pattern, transcript))
    
    output =  {
        "unique_speakers": len(speakers),
        "speakers": list(speakers)
    }
    print(f"Extracted speaker info: {output}")
    
    return output

def get_simple_classification(transcript):
    prompt = f"""
    Conversation.
    
    Transcript: 
    {transcript}... 
    
    Classify this conversation type and provide a one-sentence summary.
    """
    
    response = call_llm_api(sysprompt, prompt)
    print(f"LLM response: {response}")
    
    if isinstance(response, dict) and "text" in response:
        return response["text"]
    elif hasattr(response, "json"):
        return response.json().get("text", "Classification unavailable")
    else:
        return "Classification unavailable"