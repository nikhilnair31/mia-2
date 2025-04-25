import os
import json
import logging
import sqlite3
import datetime

logger = logging.getLogger()
logger.setLevel("INFO")

def initialize_notifications_tbl(db_filepath):
    logger.info(f"\nInitializing notifications table at: {db_filepath}")
    
    os.makedirs(os.path.dirname(db_filepath), exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS 
            NOTIFICATIONS (
                NOTIFICATION_SHOWN BOOL,
                NOTIFICATION_CONTENT TEXT,
                TIMESTAMP_STR TEXT
            )
        ''')
        conn.commit()
        conn.close()
        
        logger.info(f"Table initialized!")
        return True
    except sqlite3.Error as e:
        logger.error(f"Table initialization error: {e}")
        return False

def insert_notification_to_tbl(db_filepath, insert_data):
    logger.info(f"\nInserting into notifications table at: {db_filepath}")

    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO NOTIFICATIONS (
                NOTIFICATION_SHOWN,
                NOTIFICATION_CONTENT,
                TIMESTAMP_STR
            ) 
            VALUES (?, ?, ?)
            """,
            insert_data
        )
        conn.commit()
        logger.info(f"Data inserted!")
    except sqlite3.Error as e:
        logger.error(f"Table initialization error: {e}")
        return False

def get_recent_transcripts(db_filepath, max_transcripts_per_user = 5):
    logger.info(f"Getting last {max_transcripts_per_user} transcripts from db at: {db_filepath}")
    
    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        
        cursor.execute(
            """
                SELECT 
                    TIMESTAMP_STR, TRANSCRIPT_PROCESSED_TEXT, ANALYSIS_JSON 
                FROM TRANSCRIPTIONS
                WHERE 
                    TRANSCRIPT_RAW_TEXT IS NOT NULL 
                    AND TRANSCRIPT_RAW_TEXT <> ''
                    AND ANALYSIS_JSON LIKE '%analyzed%'
                ORDER BY TIMESTAMP_STR DESC
                LIMIT ?
            """, 
            (max_transcripts_per_user,)
        )
        
        results = cursor.fetchall()
        logger.info(f"transcripts results: {results}")
        conn.close()
        
        return results
        
    except Exception as e:
        logger.error(f"Error getting transcripts: {str(e)}")
        return [("-", "-")]
def get_recent_notifications(db_filepath, max_notifications_per_user = 5):
    logger.info(f"Getting last {max_notifications_per_user} notifications from db at: {db_filepath}")
    
    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        
        cursor.execute(
            """
                SELECT 
                    TIMESTAMP_STR, NOTIFICATION_CONTENT
                FROM NOTIFICATIONS
                WHERE 
                    NOTIFICATION_SHOWN = 1
                ORDER BY TIMESTAMP_STR DESC
                LIMIT ?
            """, 
            (max_notifications_per_user,)
        )
        
        results = cursor.fetchall()
        logger.info(f"notifications results: {results}")
        conn.close()
        
        return results
        
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        return [("-", "-")]
def get_latest_persona(db_filepath):
    logger.info(f"Getting lastest persona from db at: {db_filepath}")
    
    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        
        cursor.execute(
            """
                SELECT PERSONA_STR
                FROM PERSONAS
                ORDER BY TIMESTAMP_STR DESC
                LIMIT 1
            """
        )
        
        results = cursor.fetchall()
        # logger.info(f"results: {results}")
        persona_str = '-' if results[0][0] is None else str(results[0][0])
        # logger.info(f"persona_str: {persona_str}")
        conn.close()
        
        return persona_str
        
    except Exception as e:
        logger.error(f"Error getting personas: {str(e)}")
        return "-"