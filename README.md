# Ramble Mode V2 🤖🎙️

**Fast, accurate, multi-speaker audio transcription using OpenAI Whisper on Modal.**

Free, serverless, and always ready.

---

## 🚀 Quick Start

### Deploy

```bash
modal deploy src/ramble_mode_v2.py
```

### Transcribe Audio

```bash
curl -X POST https://your-app.modal.run/transcribe \
  -F "file=@your-audio.ogg"
```

### With Options

```bash
curl -X POST https://your-app.modal.run/transcribe \
  -F "file=@audio.mp3" \
  -F "language=en" \
  -F "task=transcribe" \
  -F "speaker_detection=true"
```

---

## ✨ Features

- ✅ **FREE** — Uses local Whisper, no API costs
- ✅ **Fast** — T4 GPU with warm containers
- ✅ **Multi-language** — Auto-detects 99 languages
- ✅ **Speaker detection** — Identifies different speakers
- ✅ **Translation** — Translate any language to English
- ✅ **Timestamps** — Segment-level timing
- ✅ **Multiple formats** — ogg, mp3, wav, m4a, etc.

---

## 📚 API Reference

### POST /transcribe

Transcribe an audio file.

**Parameters:**
- `file` (required) — Audio file
- `language` (optional) — Language code (e.g., 'en', 'es')
- `task` (optional) — 'transcribe' or 'translate'
- `speaker_detection` (optional) — true/false

**Response:**
```json
{
  "text": "Full transcription text...",
  "language": "en",
  "duration_seconds": 45.2,
  "segments": [
    {
      "speaker": "Speaker 1",
      "text": "Hello, this is a test",
      "start": 0.0,
      "end": 3.5
    }
  ],
  "status": "success",
  "speakers_detected": 2
}
```

### POST /translate

Translate audio to English.

```bash
curl -X POST https://your-app.modal.run/translate \
  -F "file=@spanish-audio.mp3"
```

---

## 🏗️ Architecture

```
Audio File → Modal GPU → Whisper → Transcription
                ↓
            T4 GPU (fast)
                ↓
            FFmpeg (format conversion)
                ↓
            Whisper Base Model
                ↓
            JSON Response
```

---

## 💰 Cost

**FREE!** Modal provides:
- 10k GPU seconds/month free
- T4 GPU is $0.000164/second
- Typical 1-minute audio = 2-3 seconds GPU time
- **Estimated: $0.01-0.05 per hour of audio**

---

## 🆚 Ramble Mode V1 (Voxtral)

| Feature | V1 (Voxtral) | V2 (Whisper) |
|---------|--------------|--------------|
| Cost | FREE | FREE |
| Accuracy | Good | Excellent |
| Languages | Limited | 99+ languages |
| Speaker detection | ❌ | ✅ |
| Translation | ❌ | ✅ |
| Reliability | Issues | ✅ Stable |
| Speed | Medium | Fast |

---

## 🎯 Use Cases

- **Voice messages** — Transcribe Telegram/WhatsApp audio
- **Meetings** — Multi-speaker transcription
- **Podcasts** — Full episode transcription
- **Interviews** — Speaker-separated text
- **Translation** — Foreign language to English

---

## 🔧 Model Sizes

| Model | Speed | Accuracy | VRAM |
|-------|-------|----------|------|
| tiny | 32x | Basic | 1GB |
| base | 16x | Good | 1GB |
| small | 6x | Better | 2GB |
| medium | 2x | Great | 5GB |
| large | 1x | Best | 10GB |

**Default: base** — Best speed/accuracy balance

---

**Built by Mind Expansion Industries** 🏛️🔥
*"Speak freely, transcribe instantly."*
