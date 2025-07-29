import re
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
    "dull": -4.5,
    "silent": -6
}

def visualize_tone_progression(srt_path, save_path=None):
    # Parse the .srt file to build segments with speaker and tone
    segments = []
    with open(srt_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    i = 0
    while i + 1 < len(lines):
        line = lines[i]
        next_line = lines[i+1]

        # Identify which line is time and which is text
        if "-->" in line:
            # Time first, then text
            time_line = line
            text_line = next_line
            i += 2
        else:
            # Text first, then time
            text_line = line
            time_line = next_line
            i += 2

        # Parse start/end time
        match = re.match(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})", time_line)
        if not match:
            continue

        def parse_time(t):
            return sum(float(x) * 60 ** i for i, x in enumerate(reversed(t.replace(',', '.').split(':'))))

        start = parse_time(match.group(1))
        end = parse_time(match.group(2))

        # Parse speaker
        speaker_match = re.match(r"^\[(.*?)\]:", text_line)
        speaker = speaker_match.group(1).strip() if speaker_match else "Unknown"

        # Parse tone (last [...] in line)
        tone_matches = re.findall(r"\[(.*?)\]", text_line)
        tone = tone_matches[-1].strip() if tone_matches else "N/A"

        segments.append({
            "start": start,
            "end": end,
            "speaker": speaker,
            "tone": tone
        })

    # ==== Visualization ====
    plt.figure(figsize=(14, 6))
    fixed_colors = ["red", "blue"]
    speakers = list({seg["speaker"] for seg in segments})
    speaker_colors = {speaker: fixed_colors[i % len(fixed_colors)] for i, speaker in enumerate(speakers)}

    for speaker in speakers:
        segs = [seg for seg in segments if seg["speaker"] == speaker]
        segs.sort(key=lambda x: x["start"])
        times, levels = [], []

        for seg in segs:
            start, end, tone = seg["start"], seg["end"], seg["tone"]
            tone_level = tone_levels.get(tone, 0)
            
            # Add horizontal line segment
            times.extend([start, end, np.nan])
            levels.extend([tone_level, tone_level, np.nan])


        plt.plot(times, levels, color=speaker_colors[speaker], linewidth=2, label=speaker)

    plt.yticks(list(tone_levels.values()), list(tone_levels.keys()))
    plt.xlabel("Time (s)")
    plt.ylabel("Tone Level")
    plt.title("Tone Progression Over Time by Speaker")
    plt.grid(True)
    plt.legend(title="Speakers")
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
            tone_series.append(tone_levels["silent"])

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
                tone_match = re.search(r"\[(.*?)\]", text_line)
                if tone_match:
                    tone = tone_match.group(1).strip()
                    segments.append({"start": start, "end": end, "tone": tone})
            else:
                print("Skipping unrecognized time format:", time_line)
            i += 2
    return segments


def generate_tone_table(srt_path, output_md="tone_table.md"):
    print("\nGenerated Tone Table:")
    md_lines = ["| Speaker | Start-End (s) | Transcript | Tone |", "|---------|----------------|------------|------|"]

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

                # Match format: [SPEAKER_01]: transcript [tone]
                speaker_match = re.match(r"^\[(.*?)\]:", text_line)
                speaker = speaker_match.group(1).strip() if speaker_match else "Unknown"

                # Extract tone from square brackets at end of sentence
                tone_matches = re.findall(r"\[(.*?)\]", text_line)
                tone = tone_matches[-1].strip() if tone_matches else "N/A"

                # Remove speaker prefix and tone annotation from text
                text = re.sub(r"^\[.*?\]:", "", text_line)         # remove [SPEAKER_X]:
                text = re.sub(r"\[.*?\]\s*$", "", text).strip()    # remove [tone] at end

                md_lines.append(f"| {speaker} | {start:.1f} - {end:.1f} | {text} | {tone} |")
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
    visualize_tone_progression(segments)
    visualize_smoothed_tone(segments, resolution=0.1, smoothing_sigma=3)
    if args.file.endswith(".srt"):
        generate_tone_table(segments, args.file)