import re
from test_llm import call_llm_api

sysprompt = """
Summarize the conversation in a single sentence and classify it as one of the following:
- Monologue: One person speaking with minimal interaction
- Interview: Clear question-answer pattern
- Discussion: Balanced exchange between participants
- Presentation: Informational delivery with some interaction
"""

def analyze_transcript(transcript):
    audio_length_seconds = get_audio_length_from_transcript(transcript)
    
    if audio_length_seconds < 10:
        return {
            "status": "ignored",
            "reason": "Audio too short",
            "length_seconds": audio_length_seconds
        }
    
    speaker_info = get_basic_speaker_info(transcript)
    
    if speaker_info["unique_speakers"] > 0:
        classification = get_simple_classification(transcript, speaker_info)
    else:
        classification = "Unknown (no clear speakers detected)"
    
    output = {
        "status": "processed",
        "length_seconds": audio_length_seconds,
        "speaker_count": speaker_info["unique_speakers"],
        "classification": classification
    }
    print(f"Analysis result: {output}")
    
    return output

def get_audio_length_from_transcript(transcript):
    timestamp_pattern = r'\[(\d{2}):(\d{2}):(\d{2})\]'
    matches = re.findall(timestamp_pattern, transcript)
    
    if not matches:
        return 0
    
    last_timestamp = matches[-1]
    hours, minutes, seconds = map(int, last_timestamp)
    output = hours * 3600 + minutes * 60 + seconds
    print(f"Extracted audio length: {output} seconds")

    return output

def get_basic_speaker_info(transcript):
    speaker_pattern = r'(Speaker \w+|Unknown):\s*'
    speakers = set(re.findall(speaker_pattern, transcript))
    
    output =  {
        "unique_speakers": len(speakers),
        "speakers": list(speakers)
    }
    print(f"Extracted speaker info: {output}")
    
    return output

def get_simple_classification(transcript, speaker_info):
    prompt = f"""
    Conversation with {speaker_info["unique_speakers"]} speakers.
    
    Transcript excerpt (beginning): 
    {transcript[:500]}... 
    
    Transcript excerpt (middle): 
    {transcript[len(transcript)//2-250:len(transcript)//2+250]}...
    
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