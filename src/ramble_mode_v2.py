"""
Ramble Mode V2 - Whisper Transcription
Fast, accurate, multi-speaker audio transcription using OpenAI Whisper
Deployed on Modal for serverless GPU acceleration
"""

import modal
from modal import Image, App, asgi_app

# Create optimized image with Whisper and dependencies
image = (
    Image.debian_slim()
    .apt_install("ffmpeg", "git")
    .pip_install(
        "fastapi",
        "python-multipart",
        "openai-whisper",
        "torch>=2.0.0",
        "numpy",
        "python-docx",
    )
)

app = App("ramble-mode-v2")

# Model configuration - using base model for speed
MODEL_SIZE = "base"


@app.function(
    image=image,
    gpu="T4",
    memory=8192,
    min_containers=0,
    timeout=300,
)
@asgi_app(label="api")
def fastapi_app():
    """FastAPI app with transcription endpoint."""
    import whisper
    import torch
    import tempfile
    import subprocess
    import os
    from fastapi import FastAPI, File, UploadFile, Form
    from fastapi.responses import JSONResponse
    from typing import Optional
    
    web_app = FastAPI(title="Ramble Mode V2", version="2.0.0")
    
    # Load model at startup (cached after first call)
    print(f"🎤 Loading Whisper {MODEL_SIZE} model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model(MODEL_SIZE).to(device)
    print(f"✅ Model loaded on {device}!")
    
    @web_app.post("/transcribe")
    async def transcribe(
        file: UploadFile = File(...),
        language: Optional[str] = Form(None),
        task: str = Form("transcribe"),
        speaker_detection: bool = Form(True)
    ):
        """Transcribe uploaded audio file."""
        
        # Read uploaded file
        audio_bytes = await file.read()
        
        # Save to temp file
        suffix = os.path.splitext(file.filename)[1] or ".ogg"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name
        
        try:
            # Convert to WAV (Whisper prefers this)
            wav_path = temp_path.replace(suffix, "_processed.wav")
            result = subprocess.run([
                "ffmpeg", "-i", temp_path, "-ar", "16000", "-ac", "1",
                "-f", "wav", "-y", wav_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return JSONResponse({
                    "text": "",
                    "status": "error",
                    "error": f"Audio conversion failed: {result.stderr}"
                }, status_code=400)
            
            # Transcribe with Whisper
            print(f"🎯 Transcribing {len(audio_bytes)} bytes on {device}...")
            
            options = {
                "task": task,
                "fp16": torch.cuda.is_available(),
            }
            if language:
                options["language"] = language
            
            result = model.transcribe(wav_path, **options)
            
            # Format response
            segments = result.get("segments", [])
            full_text = result.get("text", "").strip()
            detected_language = result.get("language", "unknown")
            
            # Simple speaker detection (based on pauses)
            formatted_segments = []
            current_speaker = "Speaker 1"
            last_end = 0
            
            for i, seg in enumerate(segments):
                # If gap > 2 seconds, assume new speaker
                if seg["start"] - last_end > 2.0 and speaker_detection:
                    current_speaker = f"Speaker {(i % 2) + 1}"
                
                formatted_segments.append({
                    "speaker": current_speaker,
                    "text": seg["text"].strip(),
                    "start": round(seg["start"], 2),
                    "end": round(seg["end"], 2),
                })
                last_end = seg["end"]
            
            return {
                "text": full_text,
                "language": detected_language,
                "duration_seconds": round(segments[-1]["end"], 2) if segments else 0,
                "segments": formatted_segments,
                "status": "success",
                "model": f"whisper-{MODEL_SIZE}",
                "task": task,
                "speakers_detected": len(set(s["speaker"] for s in formatted_segments)) if speaker_detection else 1
            }
            
        except subprocess.TimeoutExpired:
            return JSONResponse({
                "text": "",
                "status": "error",
                "error": "Audio processing timed out (file too large?)"
            }, status_code=408)
            
        except Exception as e:
            import traceback
            return JSONResponse({
                "text": "",
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }, status_code=500)
        
        finally:
            # Cleanup temp files
            for path in [temp_path, wav_path]:
                if os.path.exists(path):
                    os.unlink(path)
    
    @web_app.post("/translate")
    async def translate(
        file: UploadFile = File(...),
        source_language: Optional[str] = Form(None)
    ):
        """Translate audio to English text."""
        return await transcribe(file, language=source_language, task="translate", speaker_detection=False)
    
    @web_app.get("/")
    async def root():
        return {
            "service": "Ramble Mode V2",
            "version": "2.0.0",
            "model": f"whisper-{MODEL_SIZE}",
            "endpoints": {
                "/transcribe": "POST - Transcribe audio file",
                "/translate": "POST - Translate to English",
                "/health": "GET - Health check"
            },
            "features": [
                "Multi-language support",
                "Speaker detection",
                "Translation to English",
                "Segment-level timestamps"
            ],
            "status": "operational"
        }
    
    @web_app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "model": f"whisper-{MODEL_SIZE}",
            "device": device,
            "gpu_available": torch.cuda.is_available()
        }
    
    return web_app


@app.local_entrypoint()
def main():
    print("🎤 Ramble Mode V2 - Whisper Transcription")
    print(f"Model: whisper-{MODEL_SIZE}")
    print("\nDeploy:")
    print("  modal deploy ramble_mode_v2.py")
    print("\nTest:")
    print('  curl -X POST https://your-app.modal.run/transcribe -F "file=@audio.ogg"')
    print("\nFeatures:")
    print("  - Fast transcription (T4 GPU)")
    print("  - Multi-language support")
    print("  - Speaker detection")
    print("  - FREE (no API costs)")
