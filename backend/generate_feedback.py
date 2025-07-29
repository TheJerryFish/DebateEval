import requests

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
    prompt = (
        "You are a tone analysis assistant. Given the tone analysis of a debate audio, "
        "summarize how the speaker's emotional tone changed over time and give constructive feedback:\n\n"
        "Start-End | Tone | Transcript\n"
        "-------------------------------------\n"
    )
    for row in table_data:
        prompt += f"{row['start_end']} | {row['tone']} | {row['transcript']}\n"

    prompt += "\nProvide 2-3 sentences of general feedback for each speaker."
    return prompt

def get_transcript_feedback_from_ollama(transcript_text):
    prompt = (
        "You are a public speaking expert. Analyze the following debate speech and provide constructive feedback "
        "on clarity, structure, persuasiveness, and delivery:\n\n"
        f"{transcript_text}\n\n"
        "Give 2-3 sentences of constructive feedback for each speaker."
    )

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })

    if response.status_code == 200:
        return response.json()["response"].strip()
    return "Could not generate feedback on the transcript."