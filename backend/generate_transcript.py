import whisper
import os
import argparse

def generate_transcript(file_path, model_size="medium", output_format="srt"):
    assert os.path.isfile(file_path), f"File not found: {file_path}"
    
    print(f"Loading Whisper model: {model_size}")
    model = whisper.load_model(model_size)

    print(f"Transcribing {file_path}...")
    result = model.transcribe(file_path, verbose=True)
    full_transcript = result.get("text", "").strip()

    # Save with timestamps (srt or vtt)
    segments = result["segments"]
    if output_format == "srt":
        srt_file = file_path.rsplit(".", 1)[0] + ".srt"
        with open(srt_file, "w", encoding="utf-8") as f:
            for segment in segments:
                start = format_timestamp(segment["start"])
                end = format_timestamp(segment["end"])
                text = segment["text"].strip()
                f.write(f"{start} --> {end}\n{text}\n\n")
        print(f"SRT saved to: {srt_file}")
    return full_transcript

def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{int(seconds):02},{milliseconds:03}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to mp3/wav/m4a file")
    parser.add_argument("--model", default="medium", help="Whisper model size: tiny | base | small | medium | large")
    parser.add_argument("--format", default="srt", help="Output format: srt | vtt")
    args = parser.parse_args()

    transcript = generate_transcript(args.file, model_size=args.model, output_format=args.format)
    print("\nTranscript:")
    print(transcript)