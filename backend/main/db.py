import os
import sqlite3
import datetime

def initialize_db(db_filepath):
    print(f"\nInitializing DB at: {db_filepath}")
    
    os.makedirs(os.path.dirname(db_filepath), exist_ok=True)

    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS 
            TRANSCRIPTIONS (
                AUDIO_OBJECTKEY TEXT,
                TRANSCRIPT_RAW_JSON TEXT,
                TRANSCRIPT_RAW_TEXT TEXT,
                TRANSCRIPT_PROCESSED_TEXT TEXT,
                ANALYSIS_JSON TEXT,
                TODAY_STR TEXT,
                TIMESTAMP_STR TEXT
            )
        ''')
        conn.commit()
        conn.close()
        
        print(f"DB initialized successfully at {db_filepath}")
        return True
    except sqlite3.Error as e:
        print(f"DB initialization error: {e}")
        return False

def insert_to_database(db_filepath, insert_data):
    print(f"\nInserting to DB: {db_filepath}")
    
    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO 
            TRANSCRIPTIONS (
                AUDIO_OBJECTKEY,
                TRANSCRIPT_RAW_JSON,
                TRANSCRIPT_RAW_TEXT,
                TRANSCRIPT_PROCESSED_TEXT,
                ANALYSIS_JSON,
                TODAY_STR,
                TIMESTAMP_STR
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            insert_data
        )
        conn.commit()
        conn.close()
        
        print(f"Successfully inserted transcription data to DB")
        return True
    except sqlite3.Error as e:
        print(f"DB insert error: {e}")
        return False