import os
import logging
import sqlite3
import sqlite_vec
from typing import Dict, Any
from llm import (
    vectorize_query_text
)
from file import (
    generate_presigned_url
)

logger = logging.getLogger()
logger.setLevel("INFO")

def initialize_screenshots_tbl(db_filepath):
    logger.info(f"\nInitializing table SCREENSHOTS at: {db_filepath}")
    
    os.makedirs(os.path.dirname(db_filepath), exist_ok=True)

    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS 
            SCREENSHOTS (
                IMAGE_OBJECTKEY TEXT,
                ANALYSIS_RAW_JSON TEXT,
                ANALYSIS_RAW_TEXT TEXT,
                TIMESTAMP_STR TEXT
            )
        ''')
        conn.commit()
        conn.close()
        
        logger.info(f"Table SCREENSHOTS initialized successfully at {db_filepath}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Table SCREENSHOTS initialization error: {e}")
        return False

def query_screenshots_tbl(db_path: str, query_text: str) -> Dict[str, Any]:
    logger.info(f"\nQuerying table SCREENSHOTS at: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT IMAGE_OBJECTKEY, ANALYSIS_RAW_TEXT, TIMESTAMP_STR 
            FROM SCREENSHOTS 
            WHERE ANALYSIS_RAW_TEXT LIKE ? 
            LIMIT 5
        """, (f'%{query_text}%',))
        
        results = cursor.fetchall()
        conn.close()
        
        formatted_results = [{
            'image_objectkey': generate_presigned_url(row[0]),
            'analysis_raw_text': row[1],
            'timestamp_str': row[2]
        } for row in results]
        
        return {'results': formatted_results, 'search_type': 'text'}
        
    except Exception as e:
        raise Exception(f"Error querying table SCREENSHOTS: {str(e)}")