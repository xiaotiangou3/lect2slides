import os
import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from skimage.metrics import structural_similarity as ssim


def compute_frame_diff(gray1: np.ndarray, gray2: np.ndarray) -> Tuple[float, float]:
    """Computes SSIM and MAE between two grayscale images."""
    if gray1.shape != gray2.shape:
        gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))
    score, _ = ssim(gray1, gray2, full=True)
    mae = float(np.mean(np.abs(gray1.astype(float) - gray2.astype(float))))
    return float(score), mae


def extract_slides_from_video(
    video_path: str,
    output_dir: str = "temp/slides",
    sample_interval: float = 1.0,
    similarity_threshold: float = 0.94,
    mae_threshold: float = 6.0,
    min_slide_duration: float = 1.5,
) -> List[Dict[str, Any]]:
    """
    Extracts distinct slide frames from a video, capturing the final
    state of each slide before transition to include all bullet points.
    """
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_step = max(1, int(fps * sample_interval))

    slides: List[Dict[str, Any]] = []
    current_slide_start = 0.0
    last_sampled_timestamp = 0.0
    current_frame_cache: Optional[np.ndarray] = None
    prev_gray: Optional[np.ndarray] = None
    frame_idx = 0

    def _save_slide(end_time: float):
        nonlocal current_slide_start
        if current_frame_cache is None:
            return
        dur = end_time - current_slide_start
        if dur >= min_slide_duration or not slides:
            idx = len(slides) + 1
            path = os.path.join(output_dir, f"slide_{idx:03d}.png")
            cv2.imwrite(path, current_frame_cache)
            slides.append({
                "slide_number": idx,
                "start_time": current_slide_start,
                "end_time": end_time,
                "image_path": os.path.abspath(path),
            })
            print(f"  -> Slide {idx:02d}: [{current_slide_start:06.1f}s - {end_time:06.1f}s] ({dur:.1f}s)")

    while frame_idx < total_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            break

        timestamp = round(frame_idx / fps, 2)

        # Downscale for fast comparison
        h, w = frame.shape[:2]
        small = cv2.resize(frame, (640, int(h * (640 / w))))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

        if prev_gray is not None:
            sim, mae = compute_frame_diff(gray, prev_gray)
            if (sim < similarity_threshold) or (mae > mae_threshold):
                _save_slide(last_sampled_timestamp)
                current_slide_start = timestamp

        current_frame_cache = frame
        prev_gray = gray
        last_sampled_timestamp = timestamp
        frame_idx += frame_step

    # Save final slide
    _save_slide(last_sampled_timestamp)
    cap.release()

    print(f"[SlideExtractor] Total slides extracted: {len(slides)}")
    return slides
