import os
import argparse
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
from pydub.silence import split_on_silence, detect_silence

FFMPEG_PATH = "/opt/ffmpeg/bin/ffmpeg"
FFPROBE_PATH = "/opt/ffmpeg/bin/ffprobe"
os.environ["PATH"] = f"/opt/ffmpeg/bin:{os.environ.get('PATH', '')}"
AudioSegment.converter = FFMPEG_PATH
AudioSegment.ffprobe = FFPROBE_PATH

def preprocess_ambient_audio(file_path, output_path=None, 
                            normalize_audio=True, headroom=0.1,
                            compress_audio=True, threshold=-20, ratio=4.0, attack=5, release=50,
                            remove_silence=True, min_silence_len=500, silence_thresh=-40, keep_silence=100):
    if output_path is None:
        base_path = os.path.splitext(file_path)[0]
        output_path = f"{base_path}_processed.mp3"
    
    # Load audio file
    print(f"Loading audio file: {file_path}")
    audio = AudioSegment.from_file(file_path)
    
    # Step 1: Apply compression to reduce peaks and sudden loud sounds
    if compress_audio:
        print("Applying compression to reduce peaks and sudden sounds...")
        audio = compress_dynamic_range(audio, threshold=threshold, ratio=ratio, attack=attack, release=release)
    
    # Step 2: Normalize audio levels
    if normalize_audio:
        print("Normalizing audio levels...")
        audio = normalize(audio, headroom=headroom)
    
    # Step 3: Remove silence
    if remove_silence:
        print(f"Removing silence (threshold: {silence_thresh}dB, min length: {min_silence_len}ms)...")
        # First, detect silent sections for logging
        silent_sections = detect_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
        total_silence_ms = sum((end - start) for start, end in silent_sections)
        print(f"Detected {len(silent_sections)} silent sections, total {total_silence_ms/1000:.2f}s")
        
        # Split on silence and recombine
        chunks = split_on_silence(
            audio,
            min_silence_len=min_silence_len,
            silence_thresh=silence_thresh,
            keep_silence=keep_silence
        )
        
        if not chunks:
            print("No non-silent chunks found, returning original audio")
            audio.export(output_path, format="mp3")
            return output_path
        
        print(f"Recombining {len(chunks)} non-silent chunks...")
        processed_audio = chunks[0]
        for chunk in chunks[1:]:
            processed_audio += AudioSegment.silent(duration=keep_silence) + chunk
    else:
        processed_audio = audio
    
    # Export the processed audio
    print(f"Exporting processed audio to: {output_path}")
    processed_audio.export(output_path, format="mp3")
    
    # Calculate and report reduction in file size
    original_size = os.path.getsize(file_path)
    processed_size = os.path.getsize(output_path)
    reduction = (1 - processed_size / original_size) * 100
    print(f"File size reduced from {original_size/1024:.1f}KB to {processed_size/1024:.1f}KB ({reduction:.1f}% reduction)")
    
    return output_path

def main():
    parser = argparse.ArgumentParser(description="Preprocess ambient audio from phone microphone")
    parser.add_argument("input_file", help="Path to input audio file")
    parser.add_argument("-o", "--output", help="Path for output file (default: [input_file]_processed.mp3)")
    parser.add_argument("--no-normalize", action="store_false", dest="normalize", help="Skip audio normalization")
    parser.add_argument("--headroom", type=float, default=0.3, help="Normalization headroom (0-1)")
    parser.add_argument("--no-compress", action="store_false", dest="compress", help="Skip dynamic range compression")
    parser.add_argument("--threshold", type=float, default=-20, help="Compression threshold in dB")
    parser.add_argument("--ratio", type=float, default=4.0, help="Compression ratio")
    parser.add_argument("--attack", type=int, default=5, help="Compression attack time in ms")
    parser.add_argument("--release", type=int, default=50, help="Compression release time in ms")
    parser.add_argument("--no-silence-removal", action="store_false", dest="remove_silence", help="Skip silence removal")
    parser.add_argument("--min-silence", type=int, default=500, help="Minimum length of silence to remove (ms)")
    parser.add_argument("--silence-threshold", type=int, default=-40, help="Silence threshold in dB")
    parser.add_argument("--keep-silence", type=int, default=300, help="Amount of silence to keep around non-silent sections (ms)")
    
    args = parser.parse_args()
    
    preprocess_ambient_audio(
        args.input_file, 
        args.output,
        normalize_audio=args.normalize,
        headroom=args.headroom,
        compress_audio=args.compress,
        threshold=args.threshold,
        ratio=args.ratio,
        attack=args.attack,
        release=args.release,
        remove_silence=args.remove_silence,
        min_silence_len=args.min_silence,
        silence_thresh=args.silence_threshold,
        keep_silence=args.keep_silence
    )

if __name__ == "__main__":
    main()