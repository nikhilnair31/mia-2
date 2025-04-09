
import os
from pydub import AudioSegment
AUDIO_FILE_PATH = r"data\recording_04042024151458.mp3"

def read_audio_file():
    print(f"\nReading...")
    
    print (f"audio_file_path: {AUDIO_FILE_PATH}\n")
    
    return AUDIO_FILE_PATH
    
def len_audio(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    
    try:
        len = AudioSegment.from_file(file_path).duration_seconds
        print(f"Audio length: {len} seconds")
        return len
    except FileNotFoundError:
        print("Error: FFmpeg not found. Please install FFmpeg and add it to your PATH.")
        print("You can download FFmpeg from: https://ffmpeg.org/download.html")
        raise

if __name__ == "__main__":
    filepath = read_audio_file()
    audio_length = len_audio(filepath)
    print(f"Audio length: {audio_length} seconds")