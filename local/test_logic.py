import re
from test_llm import call_llm_api

def analyze_transcript(transcript):
   audio_length_seconds = get_audio_length_from_transcript(transcript)
   
   if audio_length_seconds < 10:
       return {
           "status": "ignored",
           "reason": "Audio too short (less than 10 seconds)",
           "length_seconds": audio_length_seconds
       }
   
   # Check for nonsense/filler content
   quality_analysis = analyze_transcript_quality(transcript)
   if not quality_analysis["is_valid"]:
       return {
           "status": "rejected",
           "reason": quality_analysis["reason"],
           "details": quality_analysis["details"]
       }
   
   # Get structured data about speakers and turns
   speaker_analysis = analyze_speakers(transcript)
   
   # Determine conversation type using LLM
   conversation_type = determine_conversation_type(transcript, speaker_analysis)
   
   return {
       "status": "analyzed",
       "length_seconds": audio_length_seconds,
       "quality": quality_analysis,
       "speakers": speaker_analysis,
       "conversation_type": conversation_type
   }

def get_audio_length_from_transcript(transcript):
   # Extract the last timestamp from transcript
   timestamp_pattern = r'\[(\d{2}):(\d{2}):(\d{2})\]'
   matches = re.findall(timestamp_pattern, transcript)
   
   if not matches:
       return 0
   
   last_timestamp = matches[-1]
   hours, minutes, seconds = map(int, last_timestamp)
   total_seconds = hours * 3600 + minutes * 60 + seconds
   
   return total_seconds

def analyze_transcript_quality(transcript):
   # Check for nonsense words, filler content, repetition
   filler_words = ["um", "uh", "like", "you know", "so", "actually"]
   filler_count = sum(transcript.lower().count(word) for word in filler_words)
   word_count = len(transcript.split())
   
   # Calculate filler word ratio
   filler_ratio = filler_count / word_count if word_count > 0 else 0
   
   # Check for repetitive patterns
   words = transcript.lower().split()
   repetition_threshold = 4
   repetitive_sequences = []
   
   for i in range(len(words) - repetition_threshold):
       sequence = words[i:i+repetition_threshold]
       if words[i+repetition_threshold:i+repetition_threshold*2] == sequence:
           repetitive_sequences.append(" ".join(sequence))
   
   # Result
   if filler_ratio > 0.5:
       return {
           "is_valid": False,
           "reason": "Excessive filler content",
           "details": {"filler_ratio": filler_ratio}
       }
   elif repetitive_sequences:
       return {
           "is_valid": False,
           "reason": "Repetitive content detected",
           "details": {"repetitive_sequences": repetitive_sequences}
       }
   else:
       return {"is_valid": True}

def analyze_speakers(transcript):
   # Extract speaker turns from transcript
   speaker_pattern = r'(Speaker \w+|Unknown):\s*([^[]+)(?=\[|$)'
   turns = re.findall(speaker_pattern, transcript)
   
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

def determine_conversation_type(transcript, speaker_analysis):
    # Extract key metrics
    speakers = speaker_analysis["speakers"]
    turn_taking = speaker_analysis["turn_taking"]
    
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
    prompt = f"""
    Analyze this transcript and determine if it's:
    1. A natural conversation between people
    2. Someone talking to themselves (self-talk)
    3. Media content (movie/TV/podcast)
    
    Key metrics:
    - Number of speakers: {turn_taking["unique_speakers"]}
    - Total speaker turns: {turn_taking["total_turns"]}
    - Is monologue: {is_monologue}
    - Is balanced conversation: {is_balanced_conversation}
    
    Transcript excerpt (first 300 chars): {transcript[:300]}...
    
    Provide your classification with reasoning.
    """
    
    data = {"text": prompt}
    response = call_llm_api(data)
    response.raise_for_status()
    llm_analysis = response.json()["analysis"]
    
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