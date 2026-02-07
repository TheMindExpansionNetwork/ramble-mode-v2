#!/usr/bin/env python3
"""
Ramble Mode V2 CLI
Fast audio transcription using Modal GPU endpoint
"""

import os
import sys
import argparse
import requests
from pathlib import Path

# Default endpoint (will be updated after deployment)
DEFAULT_ENDPOINT = "https://m1ndb0t-2045--api.modal.run"


def transcribe_file(audio_path: str, endpoint: str = None, language: str = None) -> dict:
    """
    Transcribe audio file using Modal GPU endpoint
    
    Args:
        audio_path: Path to audio file
        endpoint: Modal endpoint URL (optional)
        language: Language code (optional, auto-detect if not set)
    
    Returns:
        Transcription result dict
    """
    endpoint = endpoint or os.getenv("RAMBLE_ENDPOINT", DEFAULT_ENDPOINT)
    
    if not os.path.exists(audio_path):
        print(f"❌ File not found: {audio_path}")
        return None
    
    url = f"{endpoint}/transcribe"
    
    print(f"🎤 Uploading {audio_path}...")
    print(f"🌐 Endpoint: {endpoint}")
    
    with open(audio_path, "rb") as f:
        files = {"file": (os.path.basename(audio_path), f)}
        data = {}
        if language:
            data["language"] = language
        
        try:
            response = requests.post(url, files=files, data=data, timeout=120)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None


def print_transcription(result: dict, show_segments: bool = False):
    """Pretty print transcription result"""
    if not result or result.get("status") != "success":
        print("❌ Transcription failed")
        if result and "error" in result:
            print(f"Error: {result['error']}")
        return
    
    print("\n" + "=" * 60)
    print("🎤 TRANSCRIPTION RESULT")
    print("=" * 60)
    print(f"\n📝 Text:\n{result['text']}")
    print(f"\n🌍 Language: {result['language']}")
    print(f"⏱️  Duration: {result['duration_seconds']}s")
    print(f"🎯 Model: {result['model']}")
    
    if show_segments and result.get("segments"):
        print(f"\n📊 Segments ({len(result['segments'])}):")
        print("-" * 60)
        for seg in result["segments"]:
            print(f"[{seg['start']:6.2f}s - {seg['end']:6.2f}s] {seg['speaker']}: {seg['text']}")
    
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Ramble Mode V2 - Fast audio transcription",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic transcription
  ramble transcribe audio.ogg
  
  # Specify language
  ramble transcribe audio.ogg --language en
  
  # Show segments with speakers
  ramble transcribe audio.ogg --segments
  
  # Use custom endpoint
  ramble transcribe audio.ogg --endpoint https://your-app.modal.run
        """
    )
    
    parser.add_argument("audio_file", help="Path to audio file")
    parser.add_argument("--language", "-l", help="Language code (e.g., en, es)")
    parser.add_argument("--endpoint", "-e", help="Modal endpoint URL")
    parser.add_argument("--segments", "-s", action="store_true", help="Show segment details")
    parser.add_argument("--output", "-o", help="Save to file")
    
    args = parser.parse_args()
    
    # Transcribe
    result = transcribe_file(
        args.audio_file,
        endpoint=args.endpoint,
        language=args.language
    )
    
    if result:
        print_transcription(result, show_segments=args.segments)
        
        # Save to file if requested
        if args.output:
            with open(args.output, "w") as f:
                f.write(result["text"])
            print(f"\n💾 Saved to: {args.output}")
        
        # Also print raw text for piping
        print(f"\n📋 Raw text (for copying):\n{result['text']}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
