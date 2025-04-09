from test_audio import read_audio_file
from test_db import initialize_db, save_to_database
from test_logic import analyze_transcript
from test_stt import call_transcription_api

def start_process():
    conn = initialize_db()
    audio_filepath = read_audio_file()
    transcript = call_transcription_api(audio_filepath)
    analysis = analyze_transcript(audio_filepath, transcript)
    save_to_database(conn, audio_filepath, transcript, analysis)

if __name__ == "__main__":
    start_process()