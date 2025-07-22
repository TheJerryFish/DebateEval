import torchaudio
import torch
import torch.nn.functional as F
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification
import argparse
import json
import re

# Load model + processor
processor = AutoFeatureExtractor.from_pretrained("superb/wav2vec2-base-superb-er")
model = AutoModelForAudioClassification.from_pretrained("superb/wav2vec2-base-superb-er")
model.eval()

# Use MPS if available, else CPU
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
model.to(device)

def read_srt_intervals(srt_path):
    intervals = []
    with open(srt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    timestamp_pattern = re.compile(r"(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})")
    for line in lines:
        match = timestamp_pattern.match(line.strip())
        if match:
            h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, match.groups())
            start = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000
            end = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000
            intervals.append((start, end))
    return intervals

def load_audio(filename):
    waveform, sample_rate = torchaudio.load(filename)
    if sample_rate != 16000:
        resample = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        waveform = resample(waveform)
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0)  # Convert stereo to mono
    return waveform

def predict_emotion_segments(waveform, sr=16000, intervals=None, chunk_size=4, stride=2):
    results = []
    if intervals:
        for start_sec, end_sec in intervals:
            start_sample = int(start_sec * sr)
            end_sample = int(end_sec * sr)
            segment = waveform[start_sample:end_sample]
            inputs = processor(segment, sampling_rate=sr, return_tensors="pt", padding=True)
            input_values = {k: v.to(device) for k, v in inputs.items()}
            with torch.no_grad():
                logits = model(**input_values).logits
                probs = F.softmax(logits, dim=1)
                top2 = torch.topk(probs, k=2, dim=1)
                top_indices = top2.indices[0].tolist()
                top_confidences = top2.values[0].tolist()
                top_labels = [model.config.id2label[idx] for idx in top_indices]
            tone_label = map_emotions_to_fine_tone(top_labels, top_confidences)
            results.append({
                "start": round(start_sec, 2),
                "end": round(end_sec, 2),
                "emotion_top1": top_labels[0],
                "confidence_top1": round(top_confidences[0], 2),
                "emotion_top2": top_labels[1],
                "confidence_top2": round(top_confidences[1], 2),
                "tone": tone_label
            })
    else:
        chunk_samples = chunk_size * sr
        stride_samples = stride * sr
        for start in range(0, len(waveform) - chunk_samples + 1, stride_samples):
            segment = waveform[start:start + chunk_samples]
            inputs = processor(segment, sampling_rate=sr, return_tensors="pt", padding=True)
            input_values = {k: v.to(device) for k, v in inputs.items()}
            with torch.no_grad():
                logits = model(**input_values).logits
                probs = F.softmax(logits, dim=1)
                top2 = torch.topk(probs, k=2, dim=1)
                top_indices = top2.indices[0].tolist()
                top_confidences = top2.values[0].tolist()
                top_labels = [model.config.id2label[idx] for idx in top_indices]
            tone_label = map_emotions_to_fine_tone(top_labels, top_confidences)
            results.append({
                "start": round(start / sr, 2),
                "end": round((start + chunk_samples) / sr, 2),
                "emotion_top1": top_labels[0],
                "confidence_top1": round(top_confidences[0], 2),
                "emotion_top2": top_labels[1],
                "confidence_top2": round(top_confidences[1], 2),
                "tone": tone_label
            })
    return results

def map_emotions_to_fine_tone(top_labels, top_confidences):
    e1 = top_labels[0]
    c1 = top_confidences[0]
    e2 = top_labels[1]
    c2 = top_confidences[1]
    
    # Alias full names
    emotion_map = {"hap": "happy", "ang": "angry", "neu": "neutral", "sad": "sad", "fear": "fear"}
    e1_full = emotion_map.get(e1, e1)
    e2_full = emotion_map.get(e2, e2)

    # Determine strength
    def strength_label(c):
        if c >= 0.65: return "high"
        elif c >= 0.45: return "medium"
        else: return "low"
    
    s1 = strength_label(c1)
    s2 = strength_label(c2)
    
    gap = abs(c1 - c2)

    # Dominant Emotion (very confident etc.)
    if gap >= 0.3:
        dominant = e1_full if c1 > c2 else e2_full
        strength = s1 if c1 > c2 else s2
        return dominant_tone(dominant, strength)
    
    # Mixed Emotion
    return mixed_tone(e1_full, e2_full, c1, c2)

# Map single emotion to strong tone
def dominant_tone(emotion, strength):
    if emotion == "happy":
        return "very confident" if strength == "high" else "somewhat confident"
    elif emotion == "angry":
        return "strongly assertive" if strength == "high" else "mildly assertive"
    elif emotion == "fear":
        return "very nervous" if strength == "high" else "slightly nervous"
    elif emotion == "neutral":
        return "emotionally flat" if strength == "high" else "dull"
    elif emotion == "sad":
        return "very uncertain" if strength == "high" else "uncertain"
    return "uncertain"

# Handle emotion combinations
def mixed_tone(e1, e2, c1, c2):
    pair = {e1, e2}
    avg_conf = (c1 + c2) / 2

    if {"happy", "angry"} == pair:
        return "mildly assertive" if avg_conf < 0.6 else "strongly assertive"
    elif {"happy", "neutral"} == pair or {"happy", "sad"} == pair:
        return "somewhat uncertain" if avg_conf < 0.6 else "uncertain"
    elif {"angry", "fear"} == pair or {"sad", "fear"} == pair:
        return "slightly nervous" if avg_conf < 0.6 else "very nervous"
    elif {"neutral", "sad"} == pair or {"neutral", "fear"} == pair:
        return "emotionally flat" if avg_conf < 0.6 else "dull"
    elif {"happy", "fear"} == pair:
        return "conflicted"
    elif {"neutral", "happy"} == pair:
        return "softly confident"

    return "uncertain"

def segment_emotions(audio_path, srt_path=None, output_json=None):
    waveform = load_audio(audio_path).squeeze()
    intervals = read_srt_intervals(srt_path) if srt_path else None
    segments = predict_emotion_segments(waveform, intervals=intervals)

    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(segments, f, indent=2, ensure_ascii=False)

    if srt_path:
        with open(srt_path, "r", encoding="utf-8") as f:
            srt_lines = f.readlines()

        updated_lines = []
        segment_idx = 0
        i = 0
        while i < len(srt_lines):
            line = srt_lines[i]
            updated_lines.append(line)
            if "-->" in line and segment_idx < len(segments):
                if i + 1 < len(srt_lines):
                    tone = segments[segment_idx]["tone"]
                    text_line = srt_lines[i + 1].rstrip()
                    updated_lines.append(f"{text_line} [{tone}]\n")
                    i += 3
                    segment_idx += 1
                    continue
            i += 1

        with open(srt_path, "w", encoding="utf-8") as f:
            f.writelines(updated_lines)
        print(f"Updated SRT with tone labels: {srt_path}")
    return segments

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to MP3 or WAV file")
    parser.add_argument("--out", help="Optional JSON output")
    parser.add_argument("--srt", help="Path to .srt file for interval segmentation", default=None)
    args = parser.parse_args()

    import os
    if not args.out:
        base = os.path.splitext(os.path.basename(args.file))[0]
        args.out = f"{base}.json"

    segment_emotions(audio_path=args.file, srt_path=args.srt, output_json=args.out)