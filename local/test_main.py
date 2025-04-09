from test_audio import read_audio_file
from test_db import initialize_db, save_to_database
from test_logic import analyze_transcript, get_audio_length_from_transcript, analyze_transcript_quality, analyze_speakers, determine_conversation_type
from test_stt import call_transcription_api

def start_process():
    conn = initialize_db()
    
    audio_file_path = read_audio_file()
    # print(f"audio_file_path: {audio_file_path}\n")
    
    transcript = call_transcription_api(audio_file_path)
    # print(f"transcript: {transcript}\n")

    analysis = analyze_transcript(transcript)
    print(f"analysis: {analysis}\n")
    audio_len = get_audio_length_from_transcript(transcript)
    print(f"audio_len: {audio_len}\n")
    quality = analyze_transcript_quality(transcript)
    print(f"quality: {quality}\n")
    speakers = analyze_speakers(transcript)
    print(f"speakers: {speakers}\n")
    convo_type = determine_conversation_type(transcript, speakers)
    print(f"convo_type: {convo_type}\n")
    
    save_to_database(audio_file_path, transcript, analysis, conn)

if __name__ == "__main__":
    start_process()