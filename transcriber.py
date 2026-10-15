import re
import os
from typing import List, Dict, Any, Optional


def clean_text(text: str) -> str:
    """Strips HTML/VTT tags and normalizes whitespace."""
    return " ".join(re.sub(r"<[^>]+>", "", text).split()).strip()


def parse_vtt(vtt_path: str) -> List[Dict[str, Any]]:
    """Parses a WebVTT file, deduplicating consecutive scrolling subtitles."""
    import webvtt

    segments = []
    for caption in webvtt.read(vtt_path):
        text = clean_text(caption.text)
        if not text:
            continue

        start, end = round(caption.start_in_seconds, 2), round(caption.end_in_seconds, 2)
        if segments and segments[-1]["text"] == text:
            segments[-1]["end"] = max(segments[-1]["end"], end)
        else:
            segments.append({"start": start, "end": end, "text": text})

    return segments


def transcribe_with_whisper(
    media_path: str,
    model_size: str = "base",
    language: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Transcribes audio using faster-whisper (fallback)."""
    from faster_whisper import WhisperModel

    try:
        model = WhisperModel(model_size, device="auto", compute_type="auto")
    except Exception:
        model = WhisperModel(model_size, device="cpu", compute_type="int8")

    print(f"[Transcriber] Running Whisper '{model_size}' on: {media_path}...")
    whisper_segments, _ = model.transcribe(media_path, language=language, beam_size=5, vad_filter=True)

    segments = []
    for s in whisper_segments:
        text = clean_text(s.text)
        if text:
            segments.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": text})

    return segments


def get_transcript(
    subtitle_path: Optional[str],
    media_path: str,
    whisper_model: str = "base",
) -> List[Dict[str, Any]]:
    """Returns transcript from subtitles if available, falling back to Whisper AI."""
    if subtitle_path and os.path.isfile(subtitle_path) and os.path.getsize(subtitle_path) > 0:
        try:
            segments = parse_vtt(subtitle_path)
            if segments:
                print(f"[Transcriber] Parsed {len(segments)} subtitle segments.")
                return segments
        except Exception as e:
            print(f"[Transcriber] Subtitle parsing failed ({e}). Falling back to Whisper.")

    return transcribe_with_whisper(media_path, model_size=whisper_model)
