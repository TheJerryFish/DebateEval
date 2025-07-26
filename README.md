# 🎙️ DebateEval

**DebateEval** is an AI-powered web app that evaluates audio files for tone progression, emotional segments, and overall communication quality.

---

## 🚀 Features

- 🎧 Upload `.mp3` debate audio files
- 📝 Auto-transcribes with Whisper
- 🎭 Detects emotional tone over time (wav2vec2-based)
- 📊 Visualizes tone progression + smoothed emotion trends
- 📋 Generates a tone-marked table of speech segments
- 🧠 Uses a local LLM to:
  - Analyze tone shifts and give feedback
  - Analyze content/speech delivery quality

---


## 🧩 Tech Stack

- **Frontend:** React
- **Backend:** Flask
- **Transcription:** OpenAI Whisper
- **Emotion Detection:** `superb/wav2vec2-base-superb-er`
- **LLM Feedback:** Ollama + Mistral (local)
- **Visualization:** Matplotlib + Markdown parsing

---

## 🧪 Local Development Setup

### 🔧 Prerequisites
- Python 3.10+
- Node.js + npm
- [Ollama](https://ollama.com) installed
- FFmpeg installed

### Instructions
```bash
git clone https://github.com/yourusername/DebateEval.git
cd DebateEval
```
We would need two terminals here,
Terminal 1:
```bash
npm run start
```
Terminal 2:
```bash
cd backend
ollama run mistral
python app.py
```

### Next Steps
1. Host on web using vercel
2. Fly.io for backend and connect to local ollama to avoid user-end download
3. Improve UI
4. Allow mass mp3 uploads