import os
import sys
import json
from generate_transcript import generate_transcript as transcribe
from segment_emotions import segment_emotions
from visualize_tone import visualize_tone_progression, visualize_smoothed_tone, generate_tone_table

def process_mp3_file(audio_file, output_dir="backend/static/output"):
    os.makedirs(output_dir, exist_ok=True)

    base_filename = os.path.splitext(os.path.basename(audio_file))[0]
    srt_file = os.path.splitext(audio_file)[0] + ".srt"
    json_file = os.path.join(output_dir, f"{base_filename}.json")
    plot_path = os.path.join(output_dir, "plot.png")
    smoothed_plot_path = os.path.join(output_dir, "smoothed_plot.png")
    tone_table_path = os.path.join(output_dir, "tone_table.md")

    print("Generating transcript...")
    transcript_text = transcribe(audio_file)  # Make sure this returns the transcript string

    print("Segmenting emotions...")
    segments = segment_emotions(audio_file, srt_file)
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(segments, f, indent=2, ensure_ascii=False)

    print("Visualizing tone...")
    visualize_tone_progression(segments, save_path=plot_path)
    visualize_smoothed_tone(segments, resolution=0.1, smoothing_sigma=3, save_path=smoothed_plot_path)

    print("Generating tone table...")
    generate_tone_table(srt_file, output_md=tone_table_path)
    with open(tone_table_path, 'r', encoding='utf-8') as f:
        tone_table_md = f.read()

    # Optional: Extract basic metrics
    num_segments = len(segments)
    tones = [seg.get("emotion") for seg in segments]
    dominant_tone = max(set(tones), key=tones.count) if tones else "unknown"

    return {
        "transcript": transcript_text,
        "table": tone_table_md,
        "tone_plot": "plot.png",
        "smoothed_plot": "smoothed_plot.png",
        "metrics": {
            "segments": num_segments,
            "dominant_tone": dominant_tone,
        }
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <audio_file.mp3>")
        return
    audio_file = sys.argv[1]
    os.makedirs("static/uploads/", exist_ok=True)
    process_mp3_file(audio_file)

if __name__ == "__main__":
    main()