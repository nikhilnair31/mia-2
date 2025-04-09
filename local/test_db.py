import sqlite3
import json

DATABASE_FILE_NAME = r"data/transcripts.db"

def initialize_db():
    """Initialize the database with a simplified schema"""
    conn = sqlite3.connect(DATABASE_FILE_NAME)
    cursor = conn.cursor()
    
    # Create a more efficient table structure
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transcriptions (
        id INTEGER PRIMARY KEY,
        file_path TEXT NOT NULL,
        transcript_length_seconds INTEGER,
        speaker_count INTEGER,
        classification TEXT,
        summary TEXT,
        creation_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Create a separate table for the full transcript to avoid loading it when not needed
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transcript_content (
        transcript_id INTEGER PRIMARY KEY,
        full_transcript TEXT,
        FOREIGN KEY (transcript_id) REFERENCES transcriptions (id)
    )''')
    
    conn.commit()
    return conn

def save_to_database(audio_file_path, transcript, analysis, conn=None):
    """Save only essential information to the database"""
    print(f"\nSaving to database...")

    should_close = False
    if conn is None:
        conn = sqlite3.connect(DATABASE_FILE_NAME)
        should_close = True
    
    cursor = conn.cursor()
    
    # Extract relevant fields from analysis
    length_seconds = analysis.get("length_seconds", 0)
    speaker_count = analysis.get("speaker_count", 0)
    classification = analysis.get("classification", "Unknown")
    
    # Generate a simple summary if it's a valid transcript
    summary = "N/A"
    if analysis.get("status") == "processed" and isinstance(classification, str):
        summary = classification.split(".")[0] if "." in classification else classification
    
    # Insert the main record
    cursor.execute(
        """INSERT INTO transcriptions 
           (file_path, transcript_length_seconds, speaker_count, classification, summary) 
           VALUES (?, ?, ?, ?, ?)""",
        (str(audio_file_path), length_seconds, speaker_count, classification, summary)
    )
    
    # Get the ID of the inserted record
    transcript_id = cursor.lastrowid
    
    # Store the full transcript separately
    cursor.execute(
        "INSERT INTO transcript_content (transcript_id, full_transcript) VALUES (?, ?)",
        (transcript_id, transcript)
    )
    
    conn.commit()
    
    if should_close:
        conn.close()
    
    print(f"Saved transcript #{transcript_id} ({length_seconds} seconds, {speaker_count} speakers)")
    return transcript_id