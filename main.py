import os
import sys
from generate_transcript import generate_transcript as transcribe
from segment_emotions import segment_emotions
from visualize_tone import visualize_tone_progression, visualize_smoothed_tone
from visualize_tone import generate_tone_table


def process_mp3_file(audio_file, output_dir="static/output"):
    import json
    os.makedirs(output_dir, exist_ok=True)

    srt_file = os.path.splitext(audio_file)[0] + ".srt"
    json_file = os.path.join(output_dir, os.path.basename(os.path.splitext(audio_file)[0] + ".json"))
    plot_path = os.path.join(output_dir, "plot.png")
    smoothed_plot_path = os.path.join(output_dir, "smoothed_plot.png")
    tone_table_path = os.path.join(output_dir, "tone_table.md")

    print("Generating transcript...")
    transcribe(audio_file)

    print("Segmenting emotions...")
    segments = segment_emotions(audio_file, srt_file)
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(segments, f, indent=2, ensure_ascii=False)

    print("Visualizing tone...")
    visualize_tone_progression(segments, save_path=plot_path)
    visualize_smoothed_tone(segments, resolution=0.1, smoothing_sigma=3, save_path=smoothed_plot_path)
    generate_tone_table(segments, srt_file, output_md=tone_table_path)

    with open(tone_table_path, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <audio_file.mp3>")
        return
    audio_file = sys.argv[1]
    process_mp3_file(audio_file)

if __name__ == "__main__":
    main()