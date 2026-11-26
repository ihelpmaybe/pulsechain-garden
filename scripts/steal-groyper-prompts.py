"""Import prompt posts from groypergarden.com manifest into PulseChain Garden.

- Keeps technique prompts intact
- Rewrites GROYPER brand text → PULSE / HEX where it's poster typography
- Skips ids we already have
- Text + prompt only (no remote image scrape) unless local images exist
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

GARDEN = Path(__file__).resolve().parents[1]
SRC = GARDEN / "tmp-groyper-manifest.json"
CONTENT = GARDEN / "content"

# Brand swaps inside prompt bodies / titles (word-boundary-ish)
REPLACEMENTS = [
    (r"\bGROYPER\b", "PULSE"),
    (r"\bGroyper\b", "Pulse"),
    (r"\bgroyper\b", "pulse"),
    (r"\bGROYP\b", "HEX"),  # monolith stacked letters
]


def extract_prompt(md: str) -> tuple[str, str] | None:
    m = re.search(r"```([^\n]*)\n([\s\S]*?)```", md or "")
    if not m:
        return None
    return m.group(1).strip(), m.group(2).strip()


def adapt(text: str) -> str:
    out = text
    for pat, rep in REPLACEMENTS:
        out = re.sub(pat, rep, out)
    return out


def rewrite_content(md: str) -> str:
    """Adapt full markdown; ensure a Result blurb + prompt fence survive."""
    md = adapt(md or "")
    # Soften groyper-garden notes that don't apply
    md = re.sub(r"(?i)groyper\s*garden", "PulseChain Garden", md)
    return md


def write_text(path: Path, text: str) -> None:
    path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")


def main() -> None:
    src = json.loads(SRC.read_text(encoding="utf-8"))
    posts = src["posts"]
    existing = {p.name for p in CONTENT.iterdir() if p.is_dir()}

    added = 0
    skipped = 0
    for p in posts:
        pid = p["id"]
        prompt = extract_prompt(p.get("content", ""))
        if not prompt:
            print("SKIP no-prompt", pid)
            skipped += 1
            continue
        if pid in existing:
            # If we already have a stub without a real technique prompt, still skip —
            # don't overwrite custom RH content.
            print("SKIP exists", pid)
            skipped += 1
            continue

        post = CONTENT / pid
        post.mkdir(parents=True, exist_ok=True)

        title = adapt(p.get("title") or pid)
        tags = p.get("tags") or ["prompt"]
        # ensure discoverability
        tag_lines = list(dict.fromkeys([*tags, "prompt", "groyper-steal"]))
        date = (p.get("date") or "2026-11-25")[:10]
        hero = p.get("hero") or "center"
        content = rewrite_content(p.get("content") or "")

        # If content somehow lost the fence, rebuild minimal
        if "```" not in content:
            lang, body = prompt
            fence = f"```{lang}\n{adapt(body)}\n```" if lang else f"```\n{adapt(body)}\n```"
            content = f"## Prompt\n\n{fence}\n"

        write_text(post / "title.md", title)
        write_text(post / "tags.md", "\n".join(tag_lines))
        write_text(post / "date.md", date)
        write_text(post / "hero.md", hero if isinstance(hero, str) else "center")
        write_text(post / "content.md", content)
        print("ADD", pid, "|", title)
        added += 1

    print(f"done added={added} skipped={skipped}")


if __name__ == "__main__":
    main()
