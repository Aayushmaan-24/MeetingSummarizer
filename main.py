#!/usr/bin/env python3
"""
Smart Meeting Summarizer — 100% free, offline-first stack
  faster-whisper  → local transcription
  Ollama          → local LLM (llama3 / mistral / any model)
  rich            → beautiful terminal UI
  click           → CLI
"""

import click
import sys
from pathlib import Path
from src.transcriber import transcribe
from src.summarizer import summarize
from src.exporter import export_markdown, export_email
from src.ui import console, print_banner, print_section


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--model", "-m", default="base", show_default=True,
              help="Whisper model size: tiny / base / small / medium / large")
@click.option("--llm", "-l", default="llama3.2", show_default=True,
              help="Ollama model name (must be pulled first)")
@click.option("--output", "-o", default="outputs", show_default=True,
              help="Output directory for generated files")
@click.option("--language", default=None,
              help="Force language (e.g. en, ta, fr). Auto-detected if omitted.")
def run(input_file, model, llm, output, language):
    """
    Transcribe a meeting audio/video file and generate:

    \b
      • Structured meeting notes  (markdown)
      • Action items list         (markdown)
      • Follow-up email draft     (markdown)
    """
    print_banner()

    input_path = Path(input_file)
    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Transcribe
    print_section("1 / 3", "Transcribing audio", "mic")
    transcript = transcribe(input_path, model_size=model, language=language)

    if not transcript.strip():
        console.print("[red]Transcription returned empty text. Check your audio file.[/red]")
        sys.exit(1)

    console.print(f"[dim]Transcript length: {len(transcript.split())} words[/dim]")

    # Step 2: Summarize via local LLM
    print_section("2 / 3", f"Summarizing with {llm}", "brain")
    result = summarize(transcript, llm_model=llm)

    # Step 3: Export
    print_section("3 / 3", "Exporting outputs", "page")
    stem = input_path.stem

    notes_path      = export_markdown(result, output_dir, stem)
    email_path      = export_email(result.get("email_draft", {}), output_dir, stem)
    transcript_path = output_dir / f"{stem}_transcript.txt"
    transcript_path.write_text(transcript, encoding="utf-8")

    from rich.panel import Panel
    from rich.text import Text

    msg = Text()
    msg.append("Transcript:    ", style="bold green")
    msg.append(str(transcript_path) + "\n")
    msg.append("Meeting notes: ", style="bold green")
    msg.append(str(notes_path) + "\n")
    msg.append("Email draft:   ", style="bold green")
    msg.append(str(email_path))

    console.print(Panel(msg, title="[bold]Done[/bold]", border_style="green", padding=(1, 2)))


if __name__ == "__main__":
    run()
