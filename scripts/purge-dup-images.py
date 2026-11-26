"""Purge duplicate custom-drop posts + bulk assets.

Keep:
- every non-custom-drop post
- the lowest-numbered custom-drop-* for each fin-01 hash
- the lowest-numbered data/bulk/img-N.webp for each hash
Delete the rest of that family.
"""
from __future__ import annotations

import hashlib
import re
import shutil
from collections import defaultdict
from pathlib import Path

GARDEN = Path(__file__).resolve().parents[1]
CONTENT = GARDEN / "content"
BULK = GARDEN / "data" / "bulk"
DRY = False  # set True to report only


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def drop_num(name: str) -> int | None:
    m = re.match(r"custom-drop-(\d+)$", name)
    return int(m.group(1)) if m else None


def bulk_num(name: str) -> int | None:
    m = re.match(r"img-(\d+)\.webp$", name, re.I)
    return int(m.group(1)) if m else None


def main() -> None:
    by_hash_posts: dict[str, list[Path]] = defaultdict(list)
    for fin in CONTENT.rglob("fin-01.webp"):
        if "thumbs" in fin.parts:
            continue
        post = fin.parent
        if post.parent != CONTENT:
            continue
        try:
            by_hash_posts[sha(fin)].append(post)
        except OSError:
            pass

    by_hash_bulk: dict[str, list[Path]] = defaultdict(list)
    if BULK.exists():
        for p in BULK.glob("img-*.webp"):
            try:
                by_hash_bulk[sha(p)].append(p)
            except OSError:
                pass

    kill_posts: list[Path] = []
    keep_posts = 0
    for h, posts in by_hash_posts.items():
        drops = []
        named = []
        for p in posts:
            n = drop_num(p.name)
            if n is None:
                named.append(p)
            else:
                drops.append((n, p))
        # Prefer a tagged character/likeness plate, else lowest number
        def drop_rank(item: tuple[int, Path]) -> tuple[int, int]:
            n, p = item
            tags = ""
            title = ""
            tp = p / "tags.md"
            tit = p / "title.md"
            if tp.exists():
                tags = tp.read_text(encoding="utf-8").lower()
            if tit.exists():
                title = tit.read_text(encoding="utf-8").lower()
            blob = tags + " " + title
            priority = 0
            if any(k in blob for k in ("jimmy", "lena", "richard")):
                priority = -1  # better
            return (priority, n)

        drops.sort(key=drop_rank)
        # always keep named
        keep_posts += len(named)
        if drops:
            keep_posts += 1
            for _, p in drops[1:]:
                kill_posts.append(p)

    kill_bulk: list[Path] = []
    keep_bulk = 0
    for h, files in by_hash_bulk.items():
        numbered = []
        for p in files:
            n = bulk_num(p.name)
            if n is None:
                continue
            numbered.append((n, p))
        numbered.sort(key=lambda x: x[0])
        if not numbered:
            continue
        keep_bulk += 1
        for _, p in numbered[1:]:
            kill_bulk.append(p)

    print(f"keep_posts≈{keep_posts} kill_posts={len(kill_posts)}")
    print(f"keep_bulk≈{keep_bulk} kill_bulk={len(kill_bulk)}")

    if DRY:
        print("DRY RUN — no deletes")
        for p in kill_posts[:20]:
            print(" would rm post", p.name)
        for p in kill_bulk[:20]:
            print(" would rm bulk", p.name)
        return

    for p in kill_posts:
        if p.exists():
            shutil.rmtree(p)
            print("rm post", p.name)
    for p in kill_bulk:
        if p.exists():
            p.unlink()
            print("rm bulk", p.name)

    print("done")


if __name__ == "__main__":
    main()
