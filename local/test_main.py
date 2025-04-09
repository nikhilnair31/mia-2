from test_audio import read_audio_file
from test_db import initialize_db, save_to_database
from test_stt import call_transcription_api
from test_llm import call_llm_api

FILE_PATH = r"data\recording_04042024151458.mp3"

def start_process():
    conn = initialize_db()

    try:
        audio_data = read_audio_file(FILE_PATH)
        transcript = call_transcription_api(audio_data)
        analysis = call_llm_api(transcript)
        save_to_database(FILE_PATH, transcript, analysis, conn)
        return True
    except Exception as e:
        print(f"Error processing {FILE_PATH}: {str(e)}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    start_process()