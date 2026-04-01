<div align="center">
  
# 🎙️ Smart Meeting Summarizer

**A powerful Command-Line Interface (CLI) tool to transcribe and summarize your meetings.**
  
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![Local AI](https://img.shields.io/badge/AI-Local-success.svg)](#)
[![CLI Tool](https://img.shields.io/badge/Interface-CLI-lightgrey.svg)](#)

</div>

Transcribe any meeting recording → structured notes + action items + email draft.
**100% free. Runs offline. No API keys.**

```
audio/video file
      │
      ▼
 faster-whisper   ←── runs locally (CPU)
 (transcription)
      │
      ▼
   Ollama LLM     ←── runs locally (llama3.2 / mistral / gemma2 / etc.)
 (summarization)
      │
      ▼
 ┌────────────────────────┐
 │  meeting_notes.md      │  structured notes + action items table
 │  email_draft.md        │  ready-to-send follow-up email
 │  transcript.txt        │  raw transcript
 └────────────────────────┘
```

---

## Setup (one-time)

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `faster-whisper` also needs `ffmpeg` on your system.
> - macOS: `brew install ffmpeg`
> - Ubuntu: `sudo apt install ffmpeg`
> - Windows: download from https://ffmpeg.org/download.html

### 2. Install Ollama

Download from https://ollama.com and install for your OS.

Then pull a model:

```bash
ollama pull llama3.2        # recommended — fast, good quality (~2GB)
# or
ollama pull mistral         # alternative (~4GB)
# or
ollama pull gemma2:2b       # lightweight option (~1.6GB)
```

Start Ollama (if not already running as a service):

```bash
ollama serve
```

---

## Usage

```bash
python main.py path/to/recording.mp3
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--model` / `-m` | `base` | Whisper model size: `tiny` / `base` / `small` / `medium` / `large` |
| `--llm` / `-l` | `llama3.2` | Ollama model name |
| `--output` / `-o` | `outputs/` | Directory for generated files |
| `--language` | auto | Force language (e.g. `en`, `ta`, `fr`, `de`) |

### Examples

```bash
# Basic usage
python main.py meeting.mp3

# Larger Whisper model for better accuracy
python main.py meeting.mp4 --model small

# Use mistral instead of llama3
python main.py standup.wav --llm mistral

# Tamil meeting, save to custom folder
python main.py board_call.m4a --language ta --output results/
```

---

## Output files

Given `meeting.mp3`, you get:

```
outputs/
├── meeting_notes.md      ← structured notes with action items table
├── meeting_email.md      ← follow-up email draft (subject + body)
└── meeting_transcript.txt ← raw transcript
```

---

## Whisper model guide

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| `tiny` | 75 MB | Very fast | Basic |
| `base` | 145 MB | Fast | Good ✓ |
| `small` | 461 MB | Moderate | Better |
| `medium` | 1.5 GB | Slow | Great |
| `large` | 3 GB | Very slow | Best |

Start with `base`. Use `small` if you need better accuracy on accents.

---

## Supported formats

`.mp3` `.mp4` `.wav` `.m4a` `.ogg` `.webm` `.flac` `.mkv` `.avi`

---

## Troubleshooting

**"Connection refused" from Ollama**
→ Run `ollama serve` in a separate terminal.

**Model not found**
→ Run `ollama pull llama3.2` (or your chosen model).

**ffmpeg not found**
→ Install ffmpeg (see Setup step 1 above).

**Slow transcription**
→ Use `--model tiny` for faster (less accurate) transcription.
