# 🎙️ DebateEval

**DebateEval** is an AI-powered web application that evaluates debate audio files for tone progression, emotional segments, and overall communication quality. It uses cutting-edge speech transcription and LLM-driven feedback — all locally hosted and fully customizable.

---

## 🚀 Features

- 🎧 Upload `.mp3` debate audio files
- 📝 Auto-transcribes with Whisper
- 🎭 Detects emotional tone over time (wav2vec2-based)
- 📊 Visualizes tone progression + smoothed emotion trends
- 📋 Generates a tone-marked table of speech segments
- 🧠 Uses a local LLM (e.g., Mistral via Ollama) to:
  - Analyze tone shifts and give feedback
  - Analyze content/speech delivery quality

---


## 🧩 Tech Stack

- **Frontend:** React (Vite or CRA)
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

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/DebateEval.git
cd DebateEval