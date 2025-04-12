import os
import sqlite3

def initialize_db(db_filepath):
    print(f"\nInitializing database at: {db_filepath}")
    
    os.makedirs(os.path.dirname(db_filepath), exist_ok=True)

    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transcriptions (
                audio_objectkey TEXT PRIMARY KEY,
                transcript_json TEXT,
                transcript_text TEXT,
                analysis_json TEXT
            )
        ''')
        conn.commit()
        conn.close()
        
        print(f"Database initialized successfully at {db_filepath}")
        return True
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        return False

def save_to_database(db_filepath, audio_objectkey, transcript_data, transcript_text, analysis_data):
    print(f"\nSaving to database: {db_filepath}")
    
    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO transcriptions (audio_objectkey, transcript_json, transcript_text, analysis_json) 
            VALUES (?, ?, ?, ?)
            ''',
            (audio_objectkey, transcript_data, transcript_text, analysis_data)
        )
        conn.commit()
        conn.close()
        
        print(f"Successfully saved transcription data to database")
        return True
    except sqlite3.Error as e:
        print(f"Database save error: {e}")
        return False