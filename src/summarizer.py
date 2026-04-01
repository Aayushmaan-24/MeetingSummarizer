"""
Summarizer — uses Ollama to run a local LLM (llama3.2, mistral, gemma2, etc.)

Ollama must be running:  ollama serve
Model must be pulled:    ollama pull llama3.2
"""

import json
import re
from src.ui import console

OLLAMA_URL = "http://localhost:11434/api/generate"

SYSTEM_PROMPT = """You are an expert meeting analyst. Given a raw meeting transcript, you extract:
1. Structured meeting notes with key discussion points
2. A clean, numbered list of action items (who does what by when, if mentioned)
3. A professional follow-up email draft to send to attendees

Always respond ONLY with valid JSON matching this exact schema:
{
  "title": "string — short descriptive meeting title",
  "summary": "string — 2-3 sentence executive summary",
  "attendees": ["list of names mentioned, or empty list"],
  "key_points": ["bullet string", "bullet string", ...],
  "decisions": ["decision made", ...],
  "action_items": [
    {"task": "string", "owner": "string or Unknown", "due": "string or TBD"}
  ],
  "email_draft": {
    "subject": "string",
    "body": "string — full email body with greeting, paragraphs, sign-off"
  }
}

Do not add any text outside the JSON. No markdown fences."""


def _call_ollama(prompt: str, model: str) -> str:
    """Send a prompt to Ollama and return the full response text."""
    try:
        import urllib.request
    except ImportError:
        raise SystemExit("urllib not available — something is very wrong.")

    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False,
        "options": {"temperature": 0.2, "num_predict": 8192}
    }).encode()

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read())
            return data.get("response", "")
    except Exception as e:
        console.print(f"[red]Ollama error:[/red] {e}")
        console.print(
            "\n[yellow]Make sure Ollama is running:[/yellow]\n"
            "  [bold]ollama serve[/bold]\n"
            "  [bold]ollama pull llama3.2[/bold]   (or whichever model you chose)\n"
        )
        raise SystemExit(1)


def _extract_json(raw: str) -> dict:
    """Extract JSON from LLM response, tolerating minor formatting issues."""
    # Strip markdown fences if model ignored instructions
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()

    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        # Try to find JSON block inside the string
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass

    console.print("[yellow]Warning: LLM returned malformed JSON. Using fallback structure.[/yellow]")
    return {
        "title": "Meeting Summary",
        "summary": raw[:500],
        "attendees": [],
        "key_points": [raw[:300]],
        "decisions": [],
        "action_items": [],
        "email_draft": {
            "subject": "Meeting Summary",
            "body": raw
        }
    }


def summarize(transcript: str, llm_model: str = "llama3.2") -> dict:
    """
    Send transcript to local Ollama LLM and return structured summary dict.

    Args:
        transcript:  Raw transcript text.
        llm_model:   Ollama model name (must be pulled).

    Returns:
        Dict with keys: title, summary, attendees, key_points,
                        decisions, action_items, email_draft
    """
    # Truncate very long transcripts to ~12000 chars to stay within context
    max_chars = 12_000
    if len(transcript) > max_chars:
        console.print(f"  [dim]Transcript truncated to {max_chars} chars for context window.[/dim]")
        transcript = transcript[:max_chars] + "\n\n[... transcript truncated ...]"

    prompt = f"Here is the meeting transcript:\n\n{transcript}"

    console.print(f"  Sending to [bold]{llm_model}[/bold] via Ollama…")
    with console.status("[dim]Waiting for LLM response (this may take 30–90s)…[/dim]"):
        raw_response = _call_ollama(prompt, llm_model)

    result = _extract_json(raw_response)

    # Print a quick preview
    console.print(f"  [green]Title:[/green] {result.get('title', '—')}")
    console.print(f"  [green]Action items found:[/green] {len(result.get('action_items', []))}")

    return result
