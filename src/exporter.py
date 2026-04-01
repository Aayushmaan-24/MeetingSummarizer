"""
Exporter — writes structured meeting notes and email draft to disk as markdown.
"""

from pathlib import Path
from datetime import datetime
from src.ui import console


def export_markdown(result: dict, output_dir: Path, stem: str) -> Path:
    """
    Write full meeting notes to a markdown file.

    Sections: title, summary, attendees, key points,
              decisions, action items table.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    title        = result.get("title") or "Meeting Notes"
    summary      = result.get("summary") or ""
    attendees    = result.get("attendees") or []
    key_points   = result.get("key_points") or []
    decisions    = result.get("decisions") or []
    action_items = result.get("action_items") or []

    lines = [
        f"# {title}",
        f"\n_Generated: {now}_\n",
        "---\n",
        "## Executive Summary\n",
        summary,
        "\n---\n",
    ]

    if attendees:
        lines.append("## Attendees\n")
        for name in attendees:
            lines.append(f"- {name}")
        lines.append("")

    if key_points:
        lines.append("\n## Key Discussion Points\n")
        for pt in key_points:
            lines.append(f"- {pt}")
        lines.append("")

    if decisions:
        lines.append("\n## Decisions Made\n")
        for d in decisions:
            lines.append(f"- {d}")
        lines.append("")

    if action_items:
        lines.append("\n## Action Items\n")
        lines.append("| # | Task | Owner | Due |")
        lines.append("|---|------|-------|-----|")
        for i, item in enumerate(action_items, 1):
            task  = item.get("task", "")
            owner = item.get("owner", "Unknown")
            due   = item.get("due", "TBD")
            lines.append(f"| {i} | {task} | {owner} | {due} |")
        lines.append("")

    content = "\n".join(lines)
    path = output_dir / f"{stem}_notes.md"
    path.write_text(content, encoding="utf-8")
    console.print(f"  [green]Saved:[/green] {path}")
    return path


def export_email(email_draft: dict, output_dir: Path, stem: str) -> Path:
    """
    Write email draft to a markdown file.
    """
    email_draft = email_draft or {}
    subject = email_draft.get("subject") or "Meeting Follow-up"
    body    = email_draft.get("body") or ""

    content = f"# Email Draft\n\n**Subject:** {subject}\n\n---\n\n{body}\n"

    path = output_dir / f"{stem}_email.md"
    path.write_text(content, encoding="utf-8")
    console.print(f"  [green]Saved:[/green] {path}")
    return path
