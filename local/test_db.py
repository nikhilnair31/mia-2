import json
import sqlite3

DATABASE_FILE_NAME = r"data/transcripts.db"

def initialize_db():
    conn = sqlite3.connect(DATABASE_FILE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transcriptions (
        id INTEGER PRIMARY KEY,
        file_path TEXT,
        transcript TEXT,
        analysis TEXT
    )''')
    conn.commit()

    return conn

def save_to_database(conn, audio_filepath, transcript, analysis):
    print(f"\nSaving...")
    print(f"audio_filepath: {audio_filepath}")
    print(f"transcript: {transcript}")
    print(f"analysis: {analysis}")
    
    transcript_json = json.dumps(transcript)
    analysis_json = json.dumps(analysis)

    should_close = False
    if conn is None:
        conn = sqlite3.connect(DATABASE_FILE_NAME)
        should_close = True
    
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transcriptions (file_path, transcript, analysis) VALUES (?, ?, ?)",
        (audio_filepath, transcript_json, transcript_json)
    )
    conn.commit()
    
    if should_close:
        conn.close()
    
    print(f"\nSaved!")