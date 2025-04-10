import os
import json
import sqlite3

s3_bucket = "mia-2"
s3_object = "users/user_test/data/recording_04042024151458.mp3"
download_path = "/tmp/input.mp3"

def initialize_db(s3, db_filepath):
    if os.path.exists(db_filepath):
        s3.download_file(s3_bucket, s3_object, download_path)
    
    conn = sqlite3.connect(download_path)
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

def save_to_database(conn, db_filepath, audio_filepath, transcript, analysis):
    print(f"\nSaving...")
    # print(f"audio_filepath: {audio_filepath}")
    # print(f"transcript: {transcript}")
    # print(f"analysis: {analysis}")
    
    transcript_json = json.dumps(transcript)
    analysis_json = json.dumps(analysis)

    should_close = False
    if conn is None:
        conn = sqlite3.connect(db_filepath)
        should_close = True
    
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transcriptions (file_path, transcript, analysis) VALUES (?, ?, ?)",
        (audio_filepath, transcript_json, analysis_json)
    )
    conn.commit()
    
    if should_close:
        conn.close()
    
    print(f"\nSaved!")