import whisper
import os
import argparse
from pyannote.audio import Pipeline

def generate_transcript(file_path, model_size="medium", output_format="srt", hf_token=None):
    assert os.path.isfile(file_path), f"File not found: {file_path}"
    
    print(f"Loading Whisper model: {model_size}")
    model = whisper.load_model(model_size)

    print(f"Transcribing {file_path}...")
    result = model.transcribe(file_path, verbose=True)
    speaker_segments = diarize_speakers(file_path, hf_token)

    # Save with timestamps (srt or vtt)
    segments = result["segments"]
    if output_format == "srt":
        print("Writing transcript with speaker labels...")
        srt_file = file_path.rsplit(".", 1)[0] + ".srt"
        with open(srt_file, "w", encoding="utf-8") as f:
            for segment in segments:
                start = segment["start"]
                end = segment["end"]
                text = segment["text"].strip()
                speaker = find_speaker_for_segment(start, end, speaker_segments)
                print(f"{format_timestamp(start)} --> {format_timestamp(end)}: {speaker}")

                f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
                f.write(f"[{speaker}]: {text}\n\n")
    return result["text"]

def diarize_speakers(file_path, hf_token):
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=hf_token)
    diarization = pipeline(file_path, num_speakers=2)
    speaker_segments = []

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        speaker_segments.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })

    for seg in speaker_segments:
        print(f"Speaker {seg['speaker']} from {seg['start']:.2f}s to {seg['end']:.2f}s")

    return speaker_segments

def find_speaker_for_segment(start, end, speaker_segments):
    for seg in speaker_segments:
        # Assign speaker if there's an overlap between whisper and diarized segment
        if seg["end"] > start and seg["start"] < end:
            return seg["speaker"]
    return "Unknown"

def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{int(seconds):02},{milliseconds:03}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to mp3/wav/m4a file")
    parser.add_argument("--token", required=True, help="Hugging Face token for diarization")
    parser.add_argument("--model", default="medium", help="Whisper model size: tiny | base | small | medium | large")
    parser.add_argument("--format", default="srt", help="Output format: srt | vtt")
    args = parser.parse_args()

    transcript = generate_transcript(args.file, model_size=args.model, output_format=args.format, hf_token=args.token)
    print("\nTranscript:")
    print(transcript)
