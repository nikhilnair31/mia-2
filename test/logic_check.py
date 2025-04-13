import os
from local.test_logic import analyze_transcript

# Get the absolute path to the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Build the full path to the audio file
filepath = os.path.join(project_root, "data", "audio", "recording_15022024220423.m4a")  # Note: changed .mp3 to .m4a

# Check if file exists
if not os.path.exists(filepath):
    print(f"File does not exist at: {filepath}")
else:
    print(f"Found file at: {filepath}")

transcript = '''
 SOMETIME thank you Attach the heatulares Good evening everyone Thank you. T chin sorry no no I'm taking the out god Sh Thank you Thank you Okay Wait this movie no be? Suryavanshi Please watch it Please watch it For real? Yes I was gonna watch Bodyguard No, please watch Suryavanshi Why? Don't watch old shit again and again and again Just watch Suryavanshi It is just as brain did Okay Do you want it? I'm listening. Okay. Yes.
'''

try:
    result = analyze_transcript(filepath, transcript)  # Remove filepath parameter if not needed
    print(result)
except Exception as e:
    print(f"Error analyzing transcript: {str(e)}")