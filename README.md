# lect2slides

Convert YouTube lecture videos (including **private videos**) into clean 16:9 Google Slides presentations (`.pptx`) with timestamped transcripts placed into **Speaker Notes**.

---

## Quick Start

### 1. Prerequisites
- **Python 3.10+** & [`uv`](https://github.com/astral-sh/uv)
- **Node.js** (required by YouTube's player challenge solver)

### 2. Setup (Isolated with `uv`)
```bash
# Create venv and install dependencies
uv venv
uv pip install -r requirements.txt
```

### 3. Private Video Authentication
1. Install **[Cookie-Editor](https://microsoftedge.microsoft.com/addons/detail/cookieeditor/neaplmfkghagebokkhpjpoebhdledlfi)** in Edge (or Chrome).
2. Go to [youtube.com](https://www.youtube.com), open the extension, and click **Export**, then click **Export as Netscape**.
3. Paste the text into `cookies.txt` in this folder (it is auto-detected automatically, you can also specify a path to it using the `--cookies` option).

---

## Usage Examples

### Interactive Mode
```bash
uv run python main.py
```

### From YouTube URL
```bash
# Uses auto-detected cookies.txt and generates <Video_Title>.pptx
uv run python main.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### From Local Video (.mp4)
```bash
# Process a local lecture recording directly without downloading
uv run python main.py --local-video "lecture.mp4" -o "OutputSlides.pptx"
```

### Custom Settings
```bash
# Higher sampling rate + specific output name
uv run python main.py "https://www.youtube.com/watch?v=VIDEO_ID" --sample-interval 0.5 -o "Robotics_Lecture.pptx"
```

---

## CLI Options Reference

| Option | Default | Description |
| :--- | :--- | :--- |
| `url` | `None` | YouTube URL (launches interactive prompt if omitted). |
| `--local-video` | `None` | Path to a local `.mp4` file to process instead of downloading. |
| `--cookies` | `cookies.txt` | Path to cookie file (automatically used if present in root). |
| `--browser` | `edge` | Browser to read cookies from (`edge`, `chrome`, `firefox`). |
| `-o, --output` | `<title>.pptx` | Custom output filename. |
| `--sample-interval` | `1.0` | Frame sampling rate in seconds. |
| `--sim-threshold` | `0.94` | Structural Similarity (SSIM) threshold for slide changes. |
| `--mae-threshold` | `6.0` | Mean Absolute Error threshold for slide changes. |
| `--whisper-model` | `base` | Fallback Whisper AI model (`tiny`, `base`, `small`, `medium`). |
| `--keep-temp` | `False` | Retain temporary extracted frames and downloaded files. |

---

## Features

- **Private Video Access**: Seamless authentication via `cookies.txt` or Edge browser session.
- **Smart Slide Detection**: Captures the **final state** of each slide before transition (merges progressive bullet points into one complete slide).
- **Dual Transcript Engine**: Automatically uses YouTube subtitles; seamlessly falls back to local AI transcription (`faster-whisper`) if captions are absent.
- **Timestamped Speaker Notes**: Spoken text is aligned to each slide's timeframe (`[MM:SS] Transcript text`).
- **Google Slides Ready**: Generates standard 16:9 widescreen `.pptx` presentations that preserve full visual fidelity and notes in Google Slides.

---

## Viewing in Google Slides

1. Open [Google Drive](https://drive.google.com).
2. Drag and drop the generated `.pptx` file into Drive.
3. Right-click the file and select **Open with > Google Slides**.
4. Click **View > Show speaker notes** at the bottom to view the aligned transcript.
