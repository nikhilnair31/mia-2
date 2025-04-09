import time
import os
from test_audio import read_audio_file
from test_db import initialize_db, save_to_database
from test_logic import analyze_transcript
from test_stt import call_transcription_api

def start_process():
    """Main process with performance tracking for AWS Lambda"""
    start_time = time.time()
    
    # Initialize database
    conn = initialize_db()
    
    # Process the audio file
    try:
        # Get the audio file path
        audio_file_path = read_audio_file()
        if not os.path.exists(audio_file_path):
            print(f"Error: Audio file not found at {audio_file_path}")
            return
        
        # Transcribe the audio
        transcript = call_transcription_api(audio_file_path)
        if not transcript:
            print("Error: Transcription failed or returned empty result")
            return
        
        # Analyze the transcript
        analysis = analyze_transcript(transcript)
        
        # Log analysis status
        status = analysis.get("status", "unknown")
        if status == "ignored":
            print(f"Analysis ignored: {analysis.get('reason', 'Unknown reason')}")
        elif status == "processed":
            print(f"Analysis successful: {analysis.get('classification', 'No classification')}")
        else:
            print(f"Analysis status: {status}")
        
        # Save to database
        transcript_id = save_to_database(audio_file_path, transcript, analysis, conn)
        
        # Log execution time for Lambda monitoring
        execution_time = time.time() - start_time
        print(f"Process completed in {execution_time:.2f} seconds")
        
        return {
            "success": True,
            "transcript_id": transcript_id,
            "execution_time": execution_time,
            "status": status
        }
        
    except Exception as e:
        print(f"Error in processing: {str(e)}")
        
        # Log execution time even on failure
        execution_time = time.time() - start_time
        print(f"Process failed after {execution_time:.2f} seconds")
        
        return {
            "success": False,
            "error": str(e),
            "execution_time": execution_time
        }
    finally:
        # Ensure database connection is closed
        if conn:
            conn.close()

# Entry point for AWS Lambda
def lambda_handler(event, context):
    """AWS Lambda handler function"""
    return start_process()

# For local testing
if __name__ == "__main__":
    result = start_process()
    print(f"\nResult: {result}")