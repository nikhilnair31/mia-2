from test_audio import read_audio_file
from test_db import initialize_db, save_to_database
from test_stt import call_transcription_api
from test_llm import call_llm_api

sysprompt = """
Summarize the entire conversation into a single short sentence.
"""

def start_process():
    conn = initialize_db()
    
    audio_file_path = read_audio_file()
    # print(f"audio_file_path: {audio_file_path}\n")
    
    transcript = call_transcription_api(audio_file_path)
    # print(f"transcript: {transcript}\n")

    analysis = call_llm_api(sysprompt, transcript)
    # print(f"analysis: {analysis}\n")
    analysis_content = analysis['candidates'][0]['content']['parts'][0]['text']
    # print(f"analysis_content: {analysis_content}\n")
    
    save_to_database(audio_file_path, transcript, analysis_content, conn)

if __name__ == "__main__":
    start_process()