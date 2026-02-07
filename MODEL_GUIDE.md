# 🎤 Whisper Model Size Guide

## Quick Comparison

| Model | Speed | Accuracy | VRAM | Use Case |
|-------|-------|----------|------|----------|
| **tiny** | ⚡⚡⚡ | 🟡 Basic | 1GB | Quick tests, simple audio |
| **base** | ⚡⚡ | 🟢 Good | 1GB | **DEFAULT - balanced** |
| **small** | ⚡ | 🟢 Better | 2GB | Meetings, podcasts |
| **medium** | 🐢 | 🔵 Great | 5GB | Interviews, important calls |
| **large** | 🐌 | 🏆 Best | 10GB | Critical transcription |

## When to Use Each

### 🟡 Tiny
**Use for:** Quick tests, simple audio, single speaker
- ⚡ **Speed:** 10x faster than large
- 🎯 **Accuracy:** 70-80% (good enough for many use cases)
- 💾 **RAM:** Only 1GB needed
- 💰 **Cost:** Cheapest

**Example:** Testing the system, short voice notes

---

### 🟢 Base (DEFAULT)
**Use for:** Daily transcription, multi-speaker, accents
- ⚡ **Speed:** 4x faster than large
- 🎯 **Accuracy:** 85-90% (great for most use cases)
- 💾 **RAM:** 1GB needed
- 💰 **Cost:** Good balance

**Example:** Meeting transcription, phone calls

---

### 🟢 Small
**Use for:** Professional use, technical terms, multiple accents
- ⚡ **Speed:** 2x faster than large
- 🎯 **Accuracy:** 90-93% (professional grade)
- 💾 **RAM:** 2GB needed
- 💰 **Cost:** Moderate

**Example:** Podcasts, interviews, business calls

---

### 🔵 Medium
**Use for:** Important calls, legal/medical, critical accuracy
- ⚡ **Speed:** Slower but acceptable
- 🎯 **Accuracy:** 93-95% (near-human)
- 💾 **RAM:** 5GB needed
- 💰 **Cost:** Higher

**Example:** Court transcription, medical notes

---

### 🏆 Large
**Use for:** Maximum accuracy needed, research, archiving
- ⚡ **Speed:** Slowest (but worth it)
- 🎯 **Accuracy:** 95-98% (human-level)
- 💾 **RAM:** 10GB needed
- 💰 **Cost:** Most expensive

**Example:** Critical interviews, archival, research

## Speed Comparison

**For a 5-minute audio file:**

| Model | GPU Time | Relative |
|-------|----------|----------|
| tiny | 5 sec | 10x |
| base | 12 sec | 4x |
| small | 25 sec | 2x |
| medium | 50 sec | 1x |
| large | 100 sec | 0.5x |

## Cost on Modal (T4 GPU)

| Model | Per Hour | Per 5-Min File |
|-------|----------|----------------|
| tiny | ~$0.15 | ~$0.001 |
| base | ~$0.15 | ~$0.003 |
| small | ~$0.15 | ~$0.006 |
| medium | ~$0.30 | ~$0.025 |
| large | ~$0.60 | ~$0.10 |

## Recommendations

### **Default: Base** ✅
- Best balance of speed/accuracy
- 1GB VRAM (runs on any GPU)
- Good enough for 90% of use cases

### **Speed Priority: Tiny** ⚡
- When you need instant results
- Acceptable quality for drafts
- Great for testing

### **Quality Priority: Large** 🏆
- When accuracy is critical
- Worth the wait for important content
- Near-perfect transcription

## API Usage

```bash
# Tiny - fastest
curl -X POST https://api.modal.run/transcribe \
  -F "file=@audio.ogg" \
  -F "model=tiny"

# Base - balanced (DEFAULT)
curl -X POST https://api.modal.run/transcribe \
  -F "file=@audio.ogg" \
  -F "model=base"

# Large - best quality
curl -X POST https://api.modal.run/transcribe \
  -F "file=@audio.ogg" \
  -F "model=large"
```

## Volume Storage

Pre-download all models to Modal Volume:
```bash
modal run ramble_mode_v2_multi.py::download_models
```

This caches models so:
- ✅ No download wait on cold start
- ✅ Instant model switching
- ✅ Faster deployments
- ✅ All 5 models ready

**Storage cost:** ~15GB total (~$0.50/month)
