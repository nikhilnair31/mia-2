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

def save_to_database(audio_file_path, transcript, analysis, conn=None):
    print(f"Saving transcription and analysis to database for file: {audio_file_path}")

    should_close = False
    if conn is None:
        conn = sqlite3.connect(DATABASE_FILE_NAME)
        should_close = True
    
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transcriptions (file_path, transcript, analysis) VALUES (?, ?, ?)",
        (str(audio_file_path), transcript, analysis)
    )
    conn.commit()
    
    if should_close:
        conn.close()