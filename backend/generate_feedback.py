import requests
from collections import defaultdict

def get_feedback_from_ollama(table_data):
    prompt = generate_feedback_prompt(table_data)

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })

    if response.status_code == 200:
        return response.json()["response"].strip()
    return "Could not generate feedback."

def generate_feedback_prompt(table_data):
    # Group rows by speaker
    speaker_segments = defaultdict(list)
    for row in table_data:
        speaker_segments[row['speaker']].append(row)

    prompt = (
        "You are a tone analysis assistant. Given the tone analysis of a debate audio, "
        "summarize how each speaker's emotional tone changed over time and give constructive feedback.\n\n"
    )

    for speaker, segments in speaker_segments.items():
        prompt += f"=== {speaker} ===\n"
        prompt += "Start-End (s) | Tone | Transcript\n"
        prompt += "-------------------------------------\n"
        for seg in segments:
            prompt += f"{seg['start_end']} | {seg['tone']} | {seg['transcript']}\n"
        prompt += "\n"

    prompt += (
        "Provide 2-3 sentences of general feedback for each speaker, "
        "focusing on their tone progression and how they could improve their delivery. "
        "Time values are in seconds."
    )
    return prompt

def get_transcript_feedback_from_ollama(table_data):
    # Group transcripts by speaker and concatenate
    speaker_texts = defaultdict(list)
    for row in table_data:
        speaker_texts[row['speaker']].append(row['transcript'])

    # Build the prompt
    prompt = (
        "You are a public speaking expert. Analyze the following debate speeches "
        "and provide constructive feedback on clarity, structure, persuasiveness, and delivery.\n\n"
    )

    for speaker, texts in speaker_texts.items():
        combined_text = " ".join(texts)
        prompt += f"=== {speaker} ===\n{combined_text}\n\n"

    prompt += (
        "Provide 2-3 sentences of constructive feedback for each speaker, "
        "focusing on clarity, organization, persuasiveness, and delivery. "
        "Do not comment on tone."
    )

    # Send to Ollama
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })

    if response.status_code == 200:
        return response.json()["response"].strip()
    return "Could not generate transcript feedback."