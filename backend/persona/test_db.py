import json
import os
import sqlite3
import datetime

def initialize_personas_db(db_filepath):
    print(f"\nInitializing personas database at: {db_filepath}")
    
    os.makedirs(os.path.dirname(db_filepath), exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS personas (
            username TEXT,
            date TEXT,
            persona_json TEXT,
            created_at TEXT
        )''')
        conn.commit()
        conn.close()
        
        print(f"Database initialized successfully at {db_filepath}")
        return True
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        return False
    
def get_recent_transcripts(username, local_db_path, max_transcripts_per_user = 3):
    today_date = datetime.datetime.now().strftime('%Y-%m-%d')
    print(f"Getting transcripts for user {username} on date {today_date} from db at: {local_db_path}")
    
    try:
        conn = sqlite3.connect(local_db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """
                SELECT transcript_json, analysis_json 
                FROM transcriptions 
                WHERE created_on_date LIKE ?
            """, 
            (f"{str(today_date)}%",)
        )
        
        results = cursor.fetchall()
        print(f"Num of results: {len(results)}")
        conn.close()
        
        valid_transcripts = []
        for transcript, analysis_json in results:
            # print(f"transcript: {transcript}\nanalysis_json: {analysis_json}")
            if not transcript:
                continue
                
            if analysis_json:
                try:
                    analysis = json.loads(analysis_json)
                    print(f"analysis: {analysis}")
                    
                    if analysis.get('status') in ['rejected', 'ignored']:
                        continue
                except:
                    pass
            
            valid_transcripts.append(transcript)
            
            if len(valid_transcripts) >= max_transcripts_per_user:
                break
        
        print(f"Found {len(valid_transcripts)} valid transcripts for user {username}")
        return valid_transcripts
        
    except Exception as e:
        print(f"Error getting transcripts for user {username}: {str(e)}")
        return

def save_persona_to_db(local_db_path, username, persona):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect(local_db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO personas (
            username, 
            date, 
            persona_json, 
            created_at
        ) 
        VALUES (?, ?, ?, ?)
        """,
        (username, today, json.dumps(persona), created_at)
    )
    conn.commit()