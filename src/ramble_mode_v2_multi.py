"""
Ramble Mode V2 - Multi-Model with Volume
Pre-download all Whisper models to Modal Volume for instant access
"""

import modal
from modal import Image, App, asgi_app, Volume

# Create volume for model caching
model_volume = Volume.from_name("whisper-models", create_if_missing=True)

# Create optimized image
image = (
    Image.debian_slim()
    .apt_install("ffmpeg", "git")
    .pip_install(
        "fastapi",
        "python-multipart",
        "openai-whisper",
        "torch>=2.0.0",
        "numpy",
    )
)

app = App("ramble-mode-v2-multi")

# Available models
MODELS = {
    "tiny": {"size": "tiny", "speed": "fastest", "accuracy": "basic", "vram": "1GB"},
    "base": {"size": "base", "speed": "fast", "accuracy": "good", "vram": "1GB"},
    "small": {"size": "small", "speed": "medium", "accuracy": "better", "vram": "2GB"},
    "medium": {"size": "medium", "speed": "slow", "accuracy": "great", "vram": "5GB"},
    "large": {"size": "large", "speed": "slowest", "accuracy": "best", "vram": "10GB"},
}

DEFAULT_MODEL = "tiny"


@app.function(
    image=image,
    gpu="T4",
    memory=16384,  # 16GB for multiple models
    volumes={"/models": model_volume},
    timeout=600,
)
def download_models():
    """Pre-download all Whisper models to volume"""
    import whisper
    import os
    
    print("📥 Downloading Whisper models to volume...")
    
    for model_name in MODELS.keys():
        model_path = f"/models/whisper-{model_name}.pt"
        if os.path.exists(model_path):
            print(f"✅ {model_name}: Already cached")
        else:
            print(f"📥 {model_name}: Downloading...")
            model = whisper.load_model(model_name, download_root="/models")
            print(f"✅ {model_name}: Downloaded ({MODELS[model_name]['vram']})")
    
    print("\n🎉 All models ready!")
    return "Done"


@app.function(
    image=image,
    gpu="T4",
    memory=8192,
    volumes={"/models": model_volume},
    min_containers=0,
    timeout=300,
)
@asgi_app(label="api")
def fastapi_app():
    """FastAPI app with multi-model support"""
    import whisper
    import torch
    import tempfile
    import subprocess
    import os
    from fastapi import FastAPI, File, UploadFile, Form
    from fastapi.responses import JSONResponse
    from typing import Optional
    
    web_app = FastAPI(title="Ramble Mode V2 - Multi", version="2.1.0")
    
    # Cache for loaded models
    loaded_models = {}
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    def get_model(model_size: str):
        """Load model from volume or download"""
        if model_size not in loaded_models:
            print(f"🎤 Loading whisper-{model_size}...")
            model_path = f"/models/whisper-{model_size}.pt"
            
            if os.path.exists(model_path):
                # Load from cached volume
                loaded_models[model_size] = whisper.load_model(
                    model_size, 
                    download_root="/models"
                ).to(device)
            else:
                # Download if not cached
                loaded_models[model_size] = whisper.load_model(
                    model_size
                ).to(device)
            
            print(f"✅ Loaded on {device}")
        
        return loaded_models[model_size]
    
    @web_app.post("/transcribe")
    async def transcribe(
        file: UploadFile = File(...),
        model: str = Form(DEFAULT_MODEL),
        language: Optional[str] = Form(None),
        task: str = Form("transcribe"),
    ):
        """Transcribe with selectable model"""
        
        # Validate model
        if model not in MODELS:
            return JSONResponse({
                "error": f"Invalid model. Choose from: {list(MODELS.keys())}"
            }, status_code=400)
        
        # Read uploaded file
        audio_bytes = await file.read()
        suffix = os.path.splitext(file.filename)[1] or ".ogg"
        
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name
        
        try:
            # Convert to WAV
            wav_path = temp_path.replace(suffix, "_processed.wav")
            subprocess.run([
                "ffmpeg", "-i", temp_path, "-ar", "16000", "-ac", "1",
                "-f", "wav", "-y", wav_path
            ], capture_output=True, timeout=30)
            
            # Load model and transcribe
            model_obj = get_model(model)
            
            options = {
                "task": task,
                "fp16": torch.cuda.is_available(),
            }
            if language:
                options["language"] = language
            
            start_time = os.time() if hasattr(os, 'time') else 0
            result = model_obj.transcribe(wav_path, **options)
            
            # Format response
            return {
                "text": result.get("text", "").strip(),
                "language": result.get("language", "unknown"),
                "duration_seconds": round(result["segments"][-1]["end"], 2) if result.get("segments") else 0,
                "model": f"whisper-{model}",
                "model_info": MODELS[model],
                "status": "success",
            }
            
        except Exception as e:
            return JSONResponse({
                "error": str(e),
                "status": "error"
            }, status_code=500)
        
        finally:
            for path in [temp_path, wav_path]:
                if os.path.exists(path):
                    os.unlink(path)
    
    @web_app.get("/models")
    async def list_models():
        """List available models"""
        return {
            "models": MODELS,
            "default": DEFAULT_MODEL,
            "current_device": device
        }
    
    @web_app.get("/")
    async def root():
        return {
            "service": "Ramble Mode V2 - Multi",
            "version": "2.1.0",
            "models": list(MODELS.keys()),
            "endpoints": {
                "/transcribe": "POST - Transcribe audio (select model)",
                "/models": "GET - List available models",
            }
        }
    
    return web_app


@app.local_entrypoint()
def main():
    print("🎤 Ramble Mode V2 - Multi-Model")
    print("\nFirst run:")
    print("  modal run ramble_mode_v2_multi.py::download_models")
    print("\nThen deploy:")
    print("  modal deploy ramble_mode_v2_multi.py")
