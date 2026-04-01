#!/usr/bin/env python3
"""
demo.py — Test the summarizer WITHOUT any audio file.

Feeds a fake transcript directly to the LLM pipeline.
Great for verifying Ollama is set up correctly before using real audio.

Usage:
    python demo.py
    python demo.py --llm mistral
"""

import click
from pathlib import Path
from src.summarizer import summarize
from src.exporter import export_markdown, export_email
from src.ui import console, print_banner, print_section

FAKE_TRANSCRIPT = """
Alice: Alright everyone, let's get started. Today is the product sync for Q3 launch. 
We have Sarah, Bob, and Mike on the call.

Bob: Thanks Alice. So the main thing I wanted to cover is the backend deployment. 
We're still blocked on the database migration. We need to finish that by end of next week.

Sarah: I can take that on. I'll coordinate with the DevOps team and have it done by Friday the 15th.

Alice: Perfect. What about the landing page, Mike?

Mike: Design is done, waiting on copy from the marketing team. 
I'll follow up with them today and aim to have everything finalized by Wednesday.

Alice: Great. One more thing — we decided last week to drop the mobile app for this release 
and focus on the web version only. That decision stands. Bob, can you update the roadmap doc?

Bob: Yes, I'll update the roadmap by tomorrow EOD.

Alice: Excellent. Any blockers anyone wants to flag?

Sarah: We might need an extra server for load testing. I'll check the budget and get back to you by Monday.

Alice: Sounds good. Alright, I think that covers everything. 
Let's sync again same time next week. Thanks everyone.
"""


@click.command()
@click.option("--llm", "-l", default="llama3.2", show_default=True,
              help="Ollama model name")
@click.option("--output", "-o", default="outputs", show_default=True)
def demo(llm, output):
    """Run summarizer on a built-in sample transcript (no audio needed)."""
    print_banner()
    console.print("[dim]Running in DEMO mode — using built-in sample transcript[/dim]\n")

    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print_section("1 / 2", f"Summarizing with {llm}", "brain")
    result = summarize(FAKE_TRANSCRIPT.strip(), llm_model=llm)

    print_section("2 / 2", "Exporting outputs", "page")
    notes_path = export_markdown(result, output_dir, "demo_meeting")
    email_path = export_email(result.get("email_draft", {}), output_dir, "demo_meeting")

    from rich.panel import Panel
    from rich.text import Text

    msg = Text()
    msg.append("Meeting notes: ", style="bold green")
    msg.append(str(notes_path) + "\n")
    msg.append("Email draft:   ", style="bold green")
    msg.append(str(email_path))

    console.print(Panel(msg, title="[bold]Demo complete[/bold]", border_style="green", padding=(1, 2)))
    console.print("\n[dim]Now try it on a real file: python main.py your_meeting.mp3[/dim]")


if __name__ == "__main__":
    demo()
