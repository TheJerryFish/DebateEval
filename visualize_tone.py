import re
from datetime import datetime
import json
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import argparse
import numpy as np
from scipy.ndimage import gaussian_filter1d

# Map tone labels to numeric Y-axis levels
tone_levels = {
    "very confident": 5,
    "somewhat confident": 4,
    "strongly assertive": 3,
    "mildly assertive": 2,
    "softly confident": 1.5,
    "conflicted": 1,
    "uncertain": 0,
    "somewhat uncertain": -0.5,
    "very uncertain": -1,
    "slightly nervous": -2,
    "very nervous": -3,
    "emotionally flat": -4,
    "dull": -4.5
}

def visualize_tone_progression(segments, save_path=None):
    times = []
    levels = []
    labels = []

    for seg in segments:
        start = seg["start"]
        end = seg["end"]
        tone = seg["tone"]
        tone_level = tone_levels.get(tone, 0)

        times.extend([start, end])
        levels.extend([tone_level, tone_level])
        labels.append(((start + end)/2, tone))

    plt.figure(figsize=(14, 6))
    plt.plot(times, levels, drawstyle='steps-post', linewidth=2, color='darkorange')

    for x, tone in labels:
        plt.text(x, tone_levels.get(tone, 0) + 0.2, tone, rotation=45, fontsize=8, ha='center')

    plt.yticks(list(tone_levels.values()), list(tone_levels.keys()))
    plt.xlabel("Time (s)")
    plt.ylabel("Tone Level")
    plt.title("Tone Progression Over Time")
    plt.grid(True)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()


def visualize_smoothed_tone(segments, resolution=0.1, smoothing_sigma=3, save_path=None):
    max_time = max(seg["end"] for seg in segments)
    times = np.arange(0, max_time, resolution)
    tone_series = []

    for t in times:
        overlapping = [
            tone_levels.get(seg["tone"], 0)
            for seg in segments
            if seg["start"] <= t < seg["end"]
        ]
        if overlapping:
            tone_series.append(np.mean(overlapping))
        else:
            tone_series.append(0)

    tone_series = np.array(tone_series)
    smoothed = gaussian_filter1d(tone_series, sigma=smoothing_sigma)

    plt.figure(figsize=(14, 6))
    plt.plot(times, smoothed, color='darkorange', linewidth=2)

    plt.yticks(list(tone_levels.values()), list(tone_levels.keys()))
    plt.xlabel("Time (s)")
    plt.ylabel("Tone Level")
    plt.title("Smoothed Tone Progression Over Time")
    plt.grid(True)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()

def convert_srt_to_segments(srt_path):
    print("Reading SRT file:", srt_path)
    def parse_time(t):
        return sum(float(x) * 60 ** i for i, x in enumerate(reversed(t.replace(',', '.').split(':'))))

    segments = []
    with open(srt_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
        i = 0
        while i + 1 < len(lines):
            time_line = lines[i]
            text_line = lines[i + 1]
            match = re.match(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})", time_line)
            if match:
                start = parse_time(match.group(1))
                end = parse_time(match.group(2))
                print(f"Parsed times: {start} -> {end}")
                print("Text content:", text_line)
                tone_match = re.search(r"\[(.*?)\]", text_line)
                if tone_match:
                    tone = tone_match.group(1).strip()
                    print("Detected tone:", tone)
                    segments.append({"start": start, "end": end, "tone": tone})
            else:
                print("Skipping unrecognized time format:", time_line)
            i += 2
    print("Total segments parsed:", len(segments))
    return segments


def generate_tone_table(segments, srt_path, output_md="tone_table.md"):
    print("\nGenerated Tone Table:")
    md_lines = ["| Start-End (s) | Transcript | Tone |", "|--------------|------------|------|"]

    with open(srt_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
        i = 0
        while i + 1 < len(lines):
            time_line = lines[i]
            text_line = lines[i + 1]
            match = re.match(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})", time_line)
            if match:
                start = sum(float(x) * 60 ** j for j, x in enumerate(reversed(match.group(1).replace(',', '.').split(':'))))
                end = sum(float(x) * 60 ** j for j, x in enumerate(reversed(match.group(2).replace(',', '.').split(':'))))
                text = re.sub(r"\[.*?\]", "", text_line).strip()
                tone_match = re.search(r"\[(.*?)\]", text_line)
                tone = tone_match.group(1).strip() if tone_match else "N/A"
                line = f"{start:.1f} - {end:.1f} | {text} | {tone}"
                print(line)
                md_lines.append(f"| {start:.1f} - {end:.1f} | {text} | {tone} |")
            i += 2

    with open(output_md, 'w', encoding='utf-8') as out:
        out.write("\n".join(md_lines))
    print(f"\nSaved tone table to {output_md}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to .json or .srt file")
    args = parser.parse_args()

    if args.file.endswith(".srt"):
        segments = convert_srt_to_segments(args.file)
    else:
        with open(args.file) as f:
            segments = json.load(f)

    print("Segments loaded:", segments)
    visualize_tone_progression(segments)
    visualize_smoothed_tone(segments, resolution=0.1, smoothing_sigma=3)
    if args.file.endswith(".srt"):
        generate_tone_table(segments, args.file)