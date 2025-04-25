import os
import logging
import datetime
import sqlite3

logger = logging.getLogger()
logger.setLevel("INFO")

def initialize_screenshots_tbl(db_filepath):
    logger.info(f"\nInitializing table SCREENSHOTS at: {db_filepath}")

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

def insert_to_screenshots_tbl(db_filepath, insert_data):
    logger.info(f"\nInserting to Table SCREENSHOTS: {db_filepath}")
    
    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO 
            SCREENSHOTS (
                IMAGE_OBJECTKEY,
                ANALYSIS_RAW_JSON,
                ANALYSIS_RAW_TEXT,
                TIMESTAMP_STR
            ) 
            VALUES (?, ?, ?, ?)
            ''',
            insert_data
        )
        conn.commit()
        conn.close()
        
        logger.info(f"Successfully inserted screenshot data to table SCREENSHOTS")
        return True
    except sqlite3.Error as e:
        logger.error(f"Table SCREENSHOTS insert error: {e}")
        return False