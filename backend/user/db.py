import json
import os
import sqlite3
import datetime

def initialize_personas_tbl(db_filepath):
    print(f"\nInitializing personas table at: {db_filepath}")
    
    os.makedirs(os.path.dirname(db_filepath), exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS 
            PERSONAS (
                USERNAME TEXT,
                PERSONA_STR TEXT,
                TODAY_STR TEXT,
                TIMESTAMP_STR TEXT
            )
        ''')
        conn.commit()
        conn.close()
        
        print(f"Table initialized successfully at {db_filepath}")
        return True
    except sqlite3.Error as e:
        print(f"Table initialization error: {e}")
        return False

def insert_persona_to_tbl(db_filepath, insert_data):
    print(f"\nInserting into personas table at: {db_filepath}")

    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO PERSONAS (
                USERNAME, 
                PERSONA_STR, 
                TODAY_STR,
                TIMESTAMP_STR
            ) 
            VALUES (?, ?, ?, ?)
            """,
            insert_data
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        return False

def get_recent_transcripts(db_filepath, max_transcripts_per_user = 3):
    # Get today's date
    today_date = datetime.datetime.now().strftime('%Y-%m-%d')
    print(f"Getting transcripts on date {today_date} from db at: {db_filepath}")
    
    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        
        cursor.execute(
            """
                SELECT TRANSCRIPT_PROCESSED_TEXT, ANALYSIS_JSON 
                FROM TRANSCRIPTIONS 
                WHERE TODAY_STR LIKE ?
            """, 
            (f"{str(today_date)}%",)
        )
        
        results = cursor.fetchall()
        print(f"results: {results}\nlen(results): {len(results)}")
        conn.close()
        
        valid_transcripts = []
        for transcript, analysis_json in results:
            print(f"transcript: {transcript}\nanalysis_json: {analysis_json}")
            
            if not transcript:
                continue
                
            # if analysis_json:
            #     try:
            #         analysis = json.loads(analysis_json)
            #         print(f"analysis: {analysis}")
                    
            #         if analysis.get('status') in ['rejected', 'ignored']:
            #             continue
            #     except:
            #         pass
            
            valid_transcripts.append(transcript)
            
            if len(valid_transcripts) >= max_transcripts_per_user:
                break
        
        print(f"Found {len(valid_transcripts)} valid transcripts")
        return valid_transcripts
        
    except Exception as e:
        print(f"Error getting transcripts: {str(e)}")
        return