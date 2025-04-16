import os
import re
import json
from pydub import AudioSegment
from llm import call_llm_api

FFMPEG_PATH = "/opt/ffmpeg/bin/ffmpeg"
FFPROBE_PATH = "/opt/ffmpeg/bin/ffprobe"
os.environ["PATH"] = f"/opt/ffmpeg/bin:{os.environ.get('PATH', '')}"
AudioSegment.converter = FFMPEG_PATH
AudioSegment.ffprobe = FFPROBE_PATH

def analyze_transcript(filepath, processed_transcript):
    print(f"Analyzing processed_transcript for file: {filepath} | Processed transcript: {processed_transcript[:50]}...")

    # Create default result
    result = {
        "status": "analyzed",
        "filepath": filepath,
    }

    # 1. Check if the audio file is too short
    try:
        audio_length = get_audio_length(filepath)
        result["length_seconds"] = audio_length
        
        # If audio is too short (less than 10 seconds), return early
        if audio_length < 10:
            result["status"] = "ignored"
            result["reason"] = "Audio too short (less than 10 seconds)"
            return json.dumps(result)
    except Exception as e:
        print(f"Error checking audio length: {str(e)}")
        # Continue with analysis even if we couldn't get audio length
        result["length_seconds"] = None

    # 2. Check if speaker labels exist else create using llm
    speaker_info = get_speaker_info(processed_transcript)
    result["speakers"] = speaker_info

    # 3. Check if time stamps exist else create using llm
    transcript_with_timestamps = ensure_timestamps(processed_transcript, audio_length)
    result["transcript_processed"] = transcript_with_timestamps

    # 4. Classify the conversation type using LLM
    conversation_type = classify_conversation(transcript_with_timestamps, speaker_info)
    result["conversation_type"] = conversation_type

    # 5: Additional quality analysis
    quality_analysis = analyze_transcript_quality(transcript_with_timestamps)
    result["quality"] = quality_analysis
    if not quality_analysis["is_valid"]:
        result["status"] = "rejected"
        result["reason"] = quality_analysis["reason"]
    
    return json.dumps(result)
 
def get_audio_length(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    
    try:
        length = AudioSegment.from_file(file_path).duration_seconds
        print(f"Audio length: {length} seconds")
        return length
    except Exception as e:
        print(f"Error getting audio length: {str(e)}")
        raise

def get_speaker_info(transcript):
    # Extract speaker turns from transcript
    speaker_pattern = r'(Speaker \w+|Unknown):\s*([^[]+)(?=\[|$)'
    turns = re.findall(speaker_pattern, transcript)
    
    # If no speaker labels found, create them using LLM
    if not turns:
        print("No speaker labels found. Creating with LLM...")
        transcript_with_speakers = create_speaker_labels(transcript)
        turns = re.findall(speaker_pattern, transcript_with_speakers)
    
    speakers = {}
    speaker_sequence = []
    
    for speaker, text in turns:
        if speaker not in speakers:
            speakers[speaker] = {
                "turns": 0,
                "total_words": 0,
                "longest_turn_words": 0
            }
        
        words = len(text.split())
        speakers[speaker]["turns"] += 1
        speakers[speaker]["total_words"] += words
        speakers[speaker]["longest_turn_words"] = max(speakers[speaker]["longest_turn_words"], words)
        speaker_sequence.append(speaker)
    
    # Analyze turn-taking patterns
    turn_taking = {
        "total_turns": len(turns),
        "unique_speakers": len(speakers),
        "speaker_sequence": speaker_sequence
    }
    
    return {
        "speakers": speakers,
        "turn_taking": turn_taking
    }
def create_speaker_labels(transcript):
    system_prompt = """
    You are an expert at analyzing conversation transcripts. 
    Add appropriate speaker labels to the transcript below. 
    Use "Speaker 1:", "Speaker 2:", etc. for different speakers.
    Identify different speakers based on context, topics, and speaking style.
    Format the output as a proper transcript with speakers clearly indicated.
    """
    
    user_prompt = f"""
    Here is a transcript without speaker labels. Please add them:
    
    {transcript}
    """
    
    response = call_llm_api(system_prompt, user_prompt)
    
    if isinstance(response, dict) and "text" in response:
        return response["text"]
    elif hasattr(response, "json"):
        return response.json().get("text", transcript)
    else:
        # If LLM fails, return original with a generic speaker
        return f"Speaker 1: {transcript}"

def ensure_timestamps(transcript, audio_length):
    # Check if timestamps exist
    timestamp_pattern = r'\[(\d{2}):(\d{2}):(\d{2})\]'
    has_timestamps = bool(re.search(timestamp_pattern, transcript))
    
    if has_timestamps:
        return transcript
    
    # If no timestamps, create them
    return create_timestamps(transcript, audio_length)
def create_timestamps(transcript, audio_length):
    system_prompt = """
    You are an expert at analyzing conversation transcripts.
    Add appropriate timestamps to the transcript below.
    Use the format [MM:SS:00] at natural break points in the conversation.
    Distribute timestamps evenly across the transcript based on the total audio length.
    """
    
    user_prompt = f"""
    Here is a transcript without timestamps. 
    The total audio length is approximately {audio_length} seconds.
    Please add timestamps in the format [MM:SS:00]:
    
    {transcript}
    """
    
    response = call_llm_api(system_prompt, user_prompt)
    
    if isinstance(response, dict) and "text" in response:
        return response["text"]
    elif hasattr(response, "json"):
        return response.json().get("text", transcript)
    else:
        # If LLM fails, return original transcript
        return transcript

def classify_conversation(transcript, speaker_info):
    # Extract key metrics
    speakers = speaker_info["speakers"]
    turn_taking = speaker_info["turn_taking"]
    
    # Check for monologue
    is_monologue = False
    monologue_speaker = None
    
    if turn_taking["unique_speakers"] == 1:
        is_monologue = True
        monologue_speaker = list(speakers.keys())[0]
    else:
        # Check if one speaker dominates (80%+ of words)
        total_words = sum(spk["total_words"] for spk in speakers.values())
        for speaker, stats in speakers.items():
            if stats["total_words"] / total_words > 0.8:
                is_monologue = True
                monologue_speaker = speaker
                break
    
    # Check for balanced conversation
    is_balanced_conversation = False
    if turn_taking["unique_speakers"] >= 2 and turn_taking["total_turns"] >= 4:
        # Check if turns alternate between speakers
        alternating_pattern = True
        for i in range(2, len(turn_taking["speaker_sequence"])):
            if turn_taking["speaker_sequence"][i] == turn_taking["speaker_sequence"][i-1]:
                alternating_pattern = False
                break
        
        is_balanced_conversation = alternating_pattern
    
    # Query LLM to classify the transcript
    system_prompt = """
    Classify the conversation type and provide a brief analysis of the interaction pattern.
    Be concise but insightful about the conversation dynamics.
    """
    
    user_prompt = f"""
    Key metrics:
    - Number of speakers: {turn_taking["unique_speakers"]}
    - Total speaker turns: {turn_taking["total_turns"]}
    - Is monologue: {is_monologue}
    - Is balanced conversation: {is_balanced_conversation}
    
    Transcript (excerpt): {transcript[:1000]}... 
    
    Please classify this conversation (e.g., interview, casual conversation, presentation, etc.) 
    and provide a brief analysis of the interaction pattern.
    """
    
    response = call_llm_api(system_prompt, user_prompt)
    llm_analysis = ""
    
    if isinstance(response, dict) and "text" in response:
        llm_analysis = response["text"]
    elif hasattr(response, "json"):
        llm_analysis = response.json().get("text", "Classification unavailable")
    else:
        llm_analysis = "Classification unavailable"
    
    # Combine metrics with LLM analysis
    return {
        "metrics": {
            "is_monologue": is_monologue,
            "monologue_speaker": monologue_speaker,
            "is_balanced_conversation": is_balanced_conversation,
            "unique_speakers": turn_taking["unique_speakers"],
            "total_turns": turn_taking["total_turns"]
        },
        "llm_classification": llm_analysis
    }

def analyze_transcript_quality(transcript):
    # Run individual checks
    filler_analysis = check_filler_content(transcript)
    repetition_analysis = check_repetitive_patterns(transcript)
    improper_ending_ratio = check_line_endings(transcript)
    
    # Check for nonsensical transcript patterns
    nonsensical_indicators = [
        check_subtitle_markers(transcript),
        check_non_english_content(transcript),
        check_isolated_words(transcript),
        check_metadata_patterns(transcript),
        check_content_length(transcript),
        check_sentence_structure(transcript)
    ]
    
    # Result
    if any(nonsensical_indicators):
        return {
            "is_valid": False,
            "reason": "Nonsensical or non-conversational content detected",
            "details": {
                "has_subtitle_markers": nonsensical_indicators[0],
                "has_non_english_patterns": nonsensical_indicators[1],
                "has_isolated_words": nonsensical_indicators[2],
                "has_metadata_patterns": nonsensical_indicators[3],
                "too_short": nonsensical_indicators[4],
                "lacks_sentence_structure": nonsensical_indicators[5],
                "improper_ending_ratio": improper_ending_ratio
            }
        }
    elif filler_analysis["excessive_fillers"]:
        return {
            "is_valid": False,
            "reason": "Excessive filler content",
            "details": {"filler_ratio": filler_analysis["filler_ratio"]}
        }
    elif repetition_analysis["has_repetition"]:
        return {
            "is_valid": False,
            "reason": "Repetitive content detected",
            "details": {"repetitive_sequences": repetition_analysis["repetitive_sequences"]}
        }
    elif improper_ending_ratio > 0.7:  # If more than 70% of lines don't end properly
        return {
            "is_valid": False,
            "reason": "Transcript formatting issues detected",
            "details": {"improper_ending_ratio": improper_ending_ratio}
        }
    else:
        return {"is_valid": True}
def check_filler_content(transcript):
    filler_words = ["um", "uh", "like", "you know", "so", "actually"]
    filler_count = sum(transcript.lower().count(word) for word in filler_words)
    word_count = len(transcript.split())
    
    # Calculate filler word ratio
    filler_ratio = filler_count / word_count if word_count > 0 else 0
    
    return {
        "excessive_fillers": filler_ratio > 0.5,
        "filler_ratio": filler_ratio
    }
def check_repetitive_patterns(transcript):
    words = transcript.lower().split()
    repetition_threshold = 4
    repetitive_sequences = []
    
    for i in range(len(words) - repetition_threshold):
        sequence = words[i:i+repetition_threshold]
        if i+repetition_threshold*2 <= len(words) and words[i+repetition_threshold:i+repetition_threshold*2] == sequence:
            repetitive_sequences.append(" ".join(sequence))
    
    return {
        "has_repetition": bool(repetitive_sequences),
        "repetitive_sequences": repetitive_sequences
    }
def check_subtitle_markers(transcript):
    return bool(re.search(r'subtitled by|subtitle:|subs?:\s', transcript.lower()))
def check_non_english_content(transcript):
    # Check for non-English text patterns (excluding common phrases)
    return bool(re.findall(r'[^\x00-\x7F]{2,}', transcript) and 
        not re.search(r'conversation|dialogue|interview', transcript.lower()))
def check_isolated_words(transcript):
    word_count = len(transcript.split())
    isolated_lines = [
        line for line in transcript.split('\n') 
        if len(line.strip()) > 0 and 
        len(line.strip().split()) <= 1 and 
        not re.match(r'[.!?]', line.strip())
    ]
    
    return len(isolated_lines) > word_count / 10
def check_metadata_patterns(transcript):
    return bool(re.search(r'file:|title:|duration:|format:|codec:|resolution:', transcript.lower()))
def check_content_length(transcript):
    word_count = len(transcript.split())
    return word_count < 10
def check_sentence_structure(transcript):
    word_count = len(transcript.split())
    punctuation_count = len(re.findall(r'[.!?]', transcript))
    
    return punctuation_count < word_count / 20 and word_count > 30
def check_line_endings(transcript):
    lines = [line.strip() for line in transcript.split('\n') if line.strip()]
    
    if not lines:
        return 0.0
    
    improper_ending_lines = [line for line in lines 
                            if line and not re.search(r'[.!?",;:]$', line)]
    
    return len(improper_ending_lines) / len(lines)