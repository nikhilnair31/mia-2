from test_audio import read_audio_file
from test_db import initialize_db, save_to_database
from test_stt import call_transcription_api
from test_llm import call_llm_api

sysprompt = """
You are a helpful assistant. You will be provided with a transcript of a conversation. Your task is to analyze the conversation and provide insights based on the content. The analysis should include the following:
"""

def start_process():
    conn = initialize_db()
    
    audio_file_path = read_audio_file()
    
    transcript = call_transcription_api(audio_file_path)
    print(f"transcript: {content}")

    analysis = call_llm_api(sysprompt, transcript)
    # print(f"analysis: {analysis}")
    content = analysis['candidates'][0]['content']['parts'][0]['text']
    print(f"content: {content}")
    
    save_to_database(audio_file_path, transcript, analysis, conn)

if __name__ == "__main__":
    start_process()