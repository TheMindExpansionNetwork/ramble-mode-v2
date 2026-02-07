# Test Ramble Mode V2

# Deploy
modal deploy src/ramble_mode_v2.py

# Test transcription
curl -X POST https://your-app.modal.run/transcribe \
  -F "file=@test-audio.ogg"

# Test with speaker detection
curl -X POST https://your-app.modal.run/transcribe \
  -F "file=@meeting-recording.mp3" \
  -F "speaker_detection=true"

# Test translation
curl -X POST https://your-app.modal.run/translate \
  -F "file=@foreign-language.wav"

# Health check
curl https://your-app.modal.run/health
