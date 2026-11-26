"""Tag selected assets' post families as Richard."""
from __future__ import annotations

import hashlib
from pathlib import Path

GARDEN = Path(__file__).resolve().parents[1]
CONTENT = GARDEN / "content"

PATHS = [
    "data/img-ref/img-01.webp",
    "data/img-ref/img-02.webp",
    "data/img-ref/img-03.webp",
    "data/bulk/img-335.webp",
    "data/bulk/img-204.webp",
    "data/bulk/img-203.webp",
    "data/bulk/img-275.webp",
    "data/bulk/img-333.webp",
    "data/bulk/img-270.webp",
    "data/bulk/img-40.webp",
]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    hashes: set[str] = set()
    for rel in PATHS:
        p = GARDEN / rel
        if not p.exists():
            print("MISSING", rel)
            continue
        hashes.add(sha(p))

    posts: set[Path] = set()
    for fin in CONTENT.rglob("fin-01.webp"):
        try:
            if sha(fin) in hashes:
                posts.add(fin.parent)
        except OSError:
            pass
    # also match other non-thumb images in posts (img-01, etc.)
    for img in CONTENT.rglob("*.webp"):
        if "thumbs" in img.parts:
            continue
        try:
            if sha(img) in hashes:
                posts.add(img.parent if img.parent.name != "img-ref" else img.parent.parent)
        except OSError:
            pass

    # normalize: only content/<slug>
    posts = {p for p in posts if p.parent == CONTENT}

    print(f"hashes={len(hashes)} posts={len(posts)}")
    for post in sorted(posts, key=lambda p: p.name):
        title_p = post / "title.md"
        tags_p = post / "tags.md"
        content_p = post / "content.md"
        prev = title_p.read_text(encoding="utf-8").strip() if title_p.exists() else ""
        # don't clobber Jimmy/Lena character plates unless it's clearly RH
        if prev.lower() in {"jimmy", "lena", "jimmy + lena"} or prev.lower().startswith("jimmy"):
            print("SKIP character plate", post.name, prev)
            continue
        if "model kit" in prev.lower() or post.name == "custom-rh-model-kit-1":
            new_title = "Richard — model kit"
        elif prev and not prev.lower().startswith("garden drop"):
            new_title = prev if "richard" in prev.lower() else f"Richard — {prev}"
        else:
            new_title = "Richard"
        title_p.write_text(new_title + "\n", encoding="utf-8")
        existing = []
        if tags_p.exists():
            existing = [t.strip() for t in tags_p.read_text(encoding="utf-8").splitlines() if t.strip()]
        tags = list(dict.fromkeys(["custom", "richard-heart", "richard", *existing]))
        # drop generic dump-only noise
        tags = [t for t in tags if t not in {"drop"}]
        tags_p.write_text("\n".join(tags) + "\n", encoding="utf-8")
        body = content_p.read_text(encoding="utf-8") if content_p.exists() else ""
        if "Batch dump" in body or not body.strip():
            content_p.write_text(
                "## Result\n\n**Richard** — likeness / lifestyle plate. Use as face/body ref.\n",
                encoding="utf-8",
            )
        print("TAG", post.name, "->", new_title)


if __name__ == "__main__":
    main()
