
import os
from pydub import AudioSegment
from pydub.effects import normalize
from pydub.silence import split_on_silence

def normalize_audio(file_path, output_path=None, headroom=0.1):
   if output_path is None:
       base_path = os.path.splitext(file_path)[0]
       output_path = f"{base_path}_normalized.mp3"
   
   audio = AudioSegment.from_file(file_path)
   normalized_audio = normalize(audio, headroom=headroom)
   normalized_audio.export(output_path, format="mp3")
   
   return output_path

def trim_silence(file_path, output_path=None, min_silence_len=500, silence_thresh=-40, keep_silence=100):
   if output_path is None:
       base_path = os.path.splitext(file_path)[0]
       output_path = f"{base_path}_trimmed.mp3"
   
   audio = AudioSegment.from_file(file_path)
   
   chunks = split_on_silence(
       audio,
       min_silence_len=min_silence_len,
       silence_thresh=silence_thresh,
       keep_silence=keep_silence
   )
   
   if not chunks:
       return file_path
   
   processed_audio = chunks[0]
   for chunk in chunks[1:]:
       processed_audio += chunk
   
   processed_audio.export(output_path, format="mp3")
   return output_path