"""Ingest Cursor assets drop: hash-dedupe vs garden, add unique as posts + data/bulk."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from PIL import Image

GARDEN = Path(__file__).resolve().parents[1]
ASSETS = Path(r"C:\Users\punki\.cursor\projects\c-Users-punki-Desktop-windows-clone\assets")
CONTENT = GARDEN / "content"
BULK = GARDEN / "data" / "bulk"
DATE = "2026-11-25"


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def existing_hashes() -> set[str]:
    found: set[str] = set()
    for p in GARDEN.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            continue
        # skip node_modules / dist noise
        parts = {x.lower() for x in p.parts}
        if "node_modules" in parts or ".git" in parts:
            continue
        try:
            found.add(sha256_file(p))
        except OSError:
            pass
    return found


def drop_candidates() -> list[Path]:
    """Files from this session's dumps (timestamps in filename)."""
    out: list[Path] = []
    for p in sorted(ASSETS.iterdir()):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        name = p.name.lower()
        if "20-37-57" in name or "20-30-13" in name:
            out.append(p)
    return out


def next_slug_index() -> int:
    n = 0
    for d in CONTENT.iterdir():
        if not d.is_dir():
            continue
        m = re.match(r"custom-drop-(\d+)$", d.name)
        if m:
            n = max(n, int(m.group(1)))
    return n + 1


def guess_tags(name: str) -> str:
    tags = ["custom", "drop"]
    low = name.lower()
    # thin heuristics from known prior batches — no vision
    if "hex" in low:
        tags.append("hex")
    return "\n".join(tags)


def main() -> None:
    BULK.mkdir(parents=True, exist_ok=True)
    print("hashing existing garden images…")
    known = existing_hashes()
    print(f"known image hashes: {len(known)}")

    cands = drop_candidates()
    print(f"drop candidates: {len(cands)}")

    idx = next_slug_index()
    added = 0
    skipped = 0
    missing_dup_in_batch: set[str] = set()

    for src in cands:
        try:
            digest = sha256_file(src)
        except OSError as e:
            print("READFAIL", src.name, e)
            continue
        if digest in known or digest in missing_dup_in_batch:
            skipped += 1
            continue
        missing_dup_in_batch.add(digest)

        slug = f"custom-drop-{idx:03d}"
        post = CONTENT / slug
        post.mkdir(parents=True, exist_ok=True)

        im = Image.open(src)
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        else:
            im = im.convert("RGB")
        cover = post / "fin cover.jpg"
        im.save(cover, quality=90, optimize=True)

        # gallery copy
        bulk_name = f"{slug}{src.suffix.lower()}"
        if bulk_name.endswith(".jpeg"):
            bulk_name = bulk_name[:-5] + ".jpg"
        im.save(BULK / (slug + ".jpg"), quality=90, optimize=True)

        title = f"Garden drop {idx:03d}"
        (post / "title.md").write_text(title + "\n", encoding="utf-8")
        (post / "tags.md").write_text(guess_tags(src.name) + "\n", encoding="utf-8")
        (post / "date.md").write_text(DATE + "\n", encoding="utf-8")
        (post / "hero.md").write_text("center\n", encoding="utf-8")
        (post / "content.md").write_text(
            "## Result\n\nBatch dump for PulseChain Garden.\n",
            encoding="utf-8",
        )

        known.add(digest)
        print("ADD", slug, src.name[:60])
        idx += 1
        added += 1

    print(f"done added={added} skipped_dup={skipped} next_idx={idx}")


if __name__ == "__main__":
    main()
