"""
Transcription using faster-whisper — runs fully locally, no API key needed.

Supported input: .mp3 .mp4 .wav .m4a .ogg .webm .flac .mkv .avi
"""

from pathlib import Path
from src.ui import console


def transcribe(input_path: Path, model_size: str = "base", language: str = None) -> str:
    """
    Transcribe audio/video file to text.

    Args:
        input_path:  Path to audio or video file.
        model_size:  Whisper model — tiny/base/small/medium/large.
                     'base' is a good default (~145 MB, fast, decent accuracy).
        language:    ISO language code (e.g. 'en'). None = auto-detect.

    Returns:
        Full transcript as a single string.
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        console.print(
            "[red]faster-whisper not installed.[/red]\n"
            "Run:  [bold]pip install faster-whisper[/bold]"
        )
        raise SystemExit(1)

    console.print(f"  Loading Whisper [bold]{model_size}[/bold] model…")
    model = WhisperModel(model_size, device="auto", compute_type="int8")

    kwargs = {"beam_size": 5}
    if language:
        kwargs["language"] = language

    console.print(f"  Transcribing [bold]{input_path.name}[/bold]…")

    segments, info = model.transcribe(str(input_path), **kwargs)

    detected = info.language
    prob = round(info.language_probability * 100)
    console.print(f"  [dim]Detected language: {detected} ({prob}% confidence)[/dim]")

    lines = []
    with console.status("[dim]Processing segments…[/dim]"):
        for seg in segments:
            lines.append(seg.text.strip())

    return " ".join(lines)
