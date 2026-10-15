import os
import sys
import argparse
import shutil
import tempfile
from typing import Optional

from downloader import download_youtube_video
from transcriber import get_transcript
from extractor import extract_slides_from_video
from aligner import align_transcript_to_slides
from builder import create_presentation_from_slides


def run_pipeline(
    url: Optional[str] = None,
    local_video: Optional[str] = None,
    browser: Optional[str] = "edge",
    cookies_file: Optional[str] = None,
    output_path: Optional[str] = None,
    whisper_model: str = "base",
    sample_interval: float = 1.0,
    similarity_threshold: float = 0.94,
    mae_threshold: float = 6.0,
    keep_temp: bool = False,
) -> str:
    if not url and not local_video:
        raise ValueError("Either a YouTube URL or --local-video path must be provided.")

    work_dir = tempfile.mkdtemp(prefix="lect2slides_")
    try:
        if local_video:
            video_path = os.path.abspath(local_video)
            video_title = os.path.splitext(os.path.basename(local_video))[0]
            subtitle_path = None
        else:
            dl = download_youtube_video(
                url=url,
                output_dir=os.path.join(work_dir, "download"),
                browser=browser,
                cookies_file=cookies_file,
            )
            video_path, video_title, subtitle_path = dl["video_path"], dl["title"], dl.get("subtitle_path")

        if not output_path:
            safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in video_title).strip()
            output_path = f"{safe_title}.pptx"

        # 1. Transcript
        transcripts = get_transcript(subtitle_path, video_path, whisper_model=whisper_model)

        # 2. Slides
        slides = extract_slides_from_video(
            video_path,
            output_dir=os.path.join(work_dir, "slides"),
            sample_interval=sample_interval,
            similarity_threshold=similarity_threshold,
            mae_threshold=mae_threshold,
        )
        if not slides:
            raise RuntimeError("No slides detected in the video.")

        # 3. Align and Build
        aligned = align_transcript_to_slides(slides, transcripts)
        final_pptx = create_presentation_from_slides(aligned, output_path)

        print("\n" + "=" * 60)
        print(f"SUCCESS: {final_pptx}")
        print("Upload to Google Drive -> Open with Google Slides -> View Speaker Notes!")
        print("=" * 60 + "\n")
        return final_pptx

    finally:
        if not keep_temp and os.path.exists(work_dir):
            shutil.rmtree(work_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="Extract lecture slides to Google Slides PPTX with transcripts.")
    parser.add_argument("url", nargs="?", default=None, help="YouTube video URL")
    parser.add_argument("--browser", default="edge", help="Browser for cookies (default: edge)")
    parser.add_argument("--cookies", dest="cookies_file", default="cookies.txt" if os.path.isfile("cookies.txt") else None, help="Path to cookies.txt")
    parser.add_argument("--local-video", default=None, help="Path to local MP4")
    parser.add_argument("-o", "--output", default=None, help="Output PPTX path")
    parser.add_argument("--whisper-model", default="base", help="Whisper model fallback (default: base)")
    parser.add_argument("--sample-interval", type=float, default=1.0, help="Frame sampling interval in seconds (default: 1.0)")
    parser.add_argument("--sim-threshold", type=float, default=0.94, help="SSIM threshold (default: 0.94)")
    parser.add_argument("--mae-threshold", type=float, default=6.0, help="MAE threshold (default: 6.0)")
    parser.add_argument("--keep-temp", action="store_true", help="Keep temporary files")

    args = parser.parse_args()

    if not args.url and not args.local_video:
        url = input("Enter YouTube Video URL: ").strip()
        if not url:
            sys.exit("Error: URL required.")
        run_pipeline(url=url, cookies_file=args.cookies_file, output_path=args.output)
    else:
        run_pipeline(
            url=args.url,
            local_video=args.local_video,
            browser=args.browser,
            cookies_file=args.cookies_file,
            output_path=args.output,
            whisper_model=args.whisper_model,
            sample_interval=args.sample_interval,
            similarity_threshold=args.sim_threshold,
            mae_threshold=args.mae_threshold,
            keep_temp=args.keep_temp,
        )


if __name__ == "__main__":
    main()
