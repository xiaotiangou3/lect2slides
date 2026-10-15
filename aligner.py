from typing import List, Dict, Any


def format_timestamp(seconds: float) -> str:
    """Formats seconds into MM:SS or HH:MM:SS."""
    s = int(round(seconds))
    h, m, sec = s // 3600, (s % 3600) // 60, s % 60
    return f"{h:02d}:{m:02d}:{sec:02d}" if h else f"{m:02d}:{sec:02d}"


def align_transcript_to_slides(
    slides: List[Dict[str, Any]],
    transcript_segments: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Assigns transcript segments to each slide by timeframe."""
    if not slides:
        return []

    # Slide intervals with continuous boundaries
    intervals = []
    for i, slide in enumerate(slides):
        end = slides[i + 1]["start_time"] if i < len(slides) - 1 else slide["end_time"]
        intervals.append((slide["start_time"], end))

    buckets: List[List[Dict[str, Any]]] = [[] for _ in slides]
    for seg in transcript_segments:
        mid = (seg["start"] + seg["end"]) / 2.0
        # Find matching bucket
        for idx, (s_start, s_end) in enumerate(intervals):
            if s_start <= mid < s_end:
                buckets[idx].append(seg)
                break
        else:
            # Boundary fallback
            if mid < intervals[0][0]:
                buckets[0].append(seg)
            else:
                buckets[-1].append(seg)

    # Format notes
    for i, slide in enumerate(slides):
        time_header = f"Slide {slide['slide_number']} ({format_timestamp(slide['start_time'])} - {format_timestamp(slide['end_time'])})"
        lines = [time_header, "-" * len(time_header)]
        if buckets[i]:
            for s in buckets[i]:
                lines.append(f"[{format_timestamp(s['start'])}] {s['text']}")
        else:
            lines.append("(No spoken transcript recorded during this slide)")
        slide["notes"] = "\n".join(lines)

    return slides
