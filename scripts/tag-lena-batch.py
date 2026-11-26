"""Tag selected bulk assets' post families as Lena."""
from __future__ import annotations

import hashlib
from pathlib import Path

GARDEN = Path(__file__).resolve().parents[1]
CONTENT = GARDEN / "content"
BULK = GARDEN / "data" / "bulk"

NUMS = [342, 28, 146, 214, 211, 210, 409, 34, 408, 406, 277, 21, 141, 209, 208, 405, 338, 337]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    hashes: set[str] = set()
    for n in NUMS:
        p = BULK / f"img-{n}.webp"
        if not p.exists():
            print("MISSING bulk", n)
            continue
        hashes.add(sha(p))

    posts: set[Path] = set()
    for fin in CONTENT.rglob("fin-01.webp"):
        try:
            if sha(fin) in hashes:
                posts.add(fin.parent)
        except OSError:
            pass

    print(f"families={len(hashes)} posts={len(posts)}")
    for post in sorted(posts, key=lambda p: p.name):
        title = post / "title.md"
        tags = post / "tags.md"
        content = post / "content.md"
        prev = title.read_text(encoding="utf-8").strip() if title.exists() else ""
        # keep Jimmy if already on a dual plate
        if "jimmy" in prev.lower() or "Jimmy" in prev:
            new_title = "Jimmy + Lena"
        else:
            new_title = "Lena"
        title.write_text(new_title + "\n", encoding="utf-8")
        tag_set = ["custom", "lena", "sailor-venus"]
        if "jimmy" in new_title.lower():
            tag_set.insert(1, "jimmy")
        tags.write_text("\n".join(tag_set) + "\n", encoding="utf-8")
        if not content.exists() or "Batch dump" in content.read_text(encoding="utf-8"):
            content.write_text(
                f"## Result\n\n**{new_title}** — Hexlena / Sailor Venus plate.\n",
                encoding="utf-8",
            )
        print("TAG", post.name, "->", new_title)


if __name__ == "__main__":
    main()
