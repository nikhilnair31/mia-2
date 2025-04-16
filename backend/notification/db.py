import os
import json
import sqlite3
import datetime

def get_recent_transcripts(db_filepath, max_transcripts_per_user = 5):
    print(f"Getting last {max_transcripts_per_user} transcripts from db at: {db_filepath}")
    
    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        
        cursor.execute(
            """
                SELECT TRANSCRIPT_PROCESSED_TEXT, ANALYSIS_JSON 
                FROM TRANSCRIPTIONS
                ORDER BY TODAY_STR DESC
                LIMIT ?
            """, 
            (max_transcripts_per_user,)
        )
        # -- TRANSCRIPT_PROCESSED_TEXT IS NOT NULL
        # -- AND TRANSCRIPT_PROCESSED_TEXT <> ""
        # -- AND ANALYSIS_JSON LIKE ('%REJECTED%', '%IGNORED%') AND 
        
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
        
        print(f"Found {len(valid_transcripts)} valid transcripts")
        return valid_transcripts
        
    except Exception as e:
        print(f"Error getting transcripts: {str(e)}")
        return