import os
import sys
import glob
import shutil
from typing import Dict, Any, Optional
import yt_dlp

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = shutil.which("ffmpeg")


def download_youtube_video(
    url: str,
    output_dir: str = "temp",
    browser: Optional[str] = "edge",
    cookies_file: Optional[str] = None,
) -> Dict[str, Any]:
    """Downloads video and subtitles using yt-dlp."""
    os.makedirs(output_dir, exist_ok=True)
    video_template = os.path.join(output_dir, "%(id)s.%(ext)s")

    ydl_opts: Dict[str, Any] = {
        "outtmpl": video_template,
        "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]/best",
        "merge_output_format": "mp4",
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en.*", "en", "en-US", "en-orig"],
        "subtitlesformat": "vtt",
        "quiet": False,
        "no_warnings": False,
    }

    if FFMPEG_EXE and os.path.isfile(FFMPEG_EXE):
        ydl_opts["ffmpeg_location"] = FFMPEG_EXE

    if shutil.which("node"):
        ydl_opts["js_runtimes"] = {"node": {}}

    # Cookie precedence: explicit path > cookies.txt in cwd > browser extraction
    if cookies_file and os.path.isfile(cookies_file):
        ydl_opts["cookiefile"] = cookies_file
    elif os.path.isfile("cookies.txt"):
        ydl_opts["cookiefile"] = os.path.abspath("cookies.txt")
    elif browser:
        ydl_opts["cookiesfrombrowser"] = (browser, None, None, None)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"[Downloader] Fetching: {url}")
            info = ydl.extract_info(url, download=True)
            video_id = info.get("id", "video")
            title = info.get("title", "Lecture Slides")
            duration = info.get("duration", 0)

            # Locate downloaded video and subtitles
            video_path = os.path.join(output_dir, f"{video_id}.mp4")
            if not os.path.exists(video_path):
                matches = [f for f in glob.glob(os.path.join(output_dir, f"{video_id}.*")) if not f.endswith((".vtt", ".srt", ".part"))]
                video_path = matches[0] if matches else None

            if not video_path or not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found for ID: {video_id}")

            sub_matches = glob.glob(os.path.join(output_dir, f"{video_id}*.vtt"))
            subtitle_path = sub_matches[0] if sub_matches else None

            return {
                "id": video_id,
                "title": title,
                "video_path": video_path,
                "subtitle_path": subtitle_path,
                "duration": duration,
            }
    except yt_dlp.utils.DownloadError as e:
        if "cookies" in str(e).lower() or "private video" in str(e).lower():
            print("\n[Auth Error] YouTube denied access. Ensure cookies.txt is in the folder or Edge is closed.", file=sys.stderr)
        raise
