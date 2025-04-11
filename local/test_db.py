import os
import json
import sqlite3

def initialize_db(db_filepath):
    """Initialize the database if it doesn't exist, creating required tables"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_filepath), exist_ok=True)
        
        # Create a new database connection
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transcriptions (
                id INTEGER PRIMARY KEY,
                file_path TEXT,
                transcript TEXT,
                analysis TEXT
            )
        ''')
        conn.commit()
        conn.close()
        
        print(f"Database initialized successfully at {db_filepath}")
        return True
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        return False

def save_to_database(db_filepath, audio_filepath, transcript, analysis):
    """Save transcription and analysis results to the database"""
    print(f"\nSaving to database: {db_filepath}")
    
    try:
        # Convert to JSON strings if objects
        if not isinstance(transcript, str):
            transcript_data = json.dumps(transcript)
        else:
            transcript_data = transcript
            
        if not isinstance(analysis, str):
            analysis_data = json.dumps(analysis)
        else:
            analysis_data = analysis
        
        # Connect and insert
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO transcriptions (file_path, transcript, analysis) 
            VALUES (?, ?, ?)
            ''',
            (str(audio_filepath), transcript_data, analysis_data)
        )
        conn.commit()
        conn.close()
        
        print(f"Successfully saved transcription data to database")
        return True
    except sqlite3.Error as e:
        print(f"Database save error: {e}")
        return False