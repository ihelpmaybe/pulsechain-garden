"""Selective rembg cutouts from Telegram New folder.

Cut: isolated subject on plain white/black studio (sticker-ready).
Keep: scenes, memes with baked UI, screenshots, framed collages.
Updates matching garden posts in place (fin = cutout, img = original).
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import numpy as np
from PIL import Image
from rembg import remove

GARDEN = Path(__file__).resolve().parents[1]
TG = Path(r"c:\Users\punki\Downloads\Telegram Desktop\New folder")
ASSETS = Path(r"C:\Users\punki\.cursor\projects\c-Users-punki-Desktop-windows-clone\assets")
CONTENT = GARDEN / "content"
CUTOUTS = GARDEN / "data" / "cutouts"
DATE = "2026-11-25"

# Hard keep — screenshots / finished composites (do not rembg)
FORCE_KEEP = {
    "photo_11_2026-11-25_20-46-48.jpg",  # X profile screenshot
    "photo_51_2026-11-25_20-46-49.jpg",  # Costco meme scene
    "photo_58_2026-11-25_20-46-49.jpg",  # X post screenshot
    "photo_5_2026-11-25_20-46-48.jpg",  # already black void graphic
    "photo_74_2026-11-25_20-46-49.jpg",  # pink heart frame collage
    "photo_30_2026-11-25_20-46-49.jpg",  # already black cutout crop
}


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def fingerprint(im: Image.Image, size: int = 48) -> np.ndarray:
    small = im.convert("RGB").resize((size, size), Image.Resampling.BILINEAR)
    return np.asarray(small, dtype=np.float32).reshape(-1)


def fp_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.abs(a - b)))


def classify(path: Path) -> tuple[str, str]:
    if path.name in FORCE_KEEP:
        return "keep", "force-keep"
    if path.stat().st_size < 20_000:
        return "skip", "tiny-bytes"
    im = Image.open(path).convert("RGB")
    a = np.asarray(im, dtype=np.float32)
    h, w, _ = a.shape
    if min(h, w) < 280:
        return "skip", "tiny-dims"

    band = max(6, min(h, w) // 40)
    borders = np.concatenate(
        [
            a[:band].reshape(-1, 3),
            a[-band:].reshape(-1, 3),
            a[:, :band].reshape(-1, 3),
            a[:, -band:].reshape(-1, 3),
        ]
    )
    bstd = float(borders.std(axis=0).mean())
    bmean = float(borders.mean())

    # white / near-white fraction of whole image
    white = float(np.mean(np.all(a > 245, axis=2)))
    black = float(np.mean(np.all(a < 12, axis=2)))

    # phone screenshot: tall + dark chrome top strip with mid luminance noise
    aspect = h / max(w, 1)
    top = a[: max(24, h // 35)]
    top_std = float(top.std())
    if aspect > 1.85 and top_std > 35 and bmean < 80:
        return "keep", "likely-screenshot"

    # sticker on white
    if white > 0.28 and bstd < 55:
        return "cut", f"white-field white={white:.2f} bstd={bstd:.0f}"
    if bmean > 230 and bstd < 25:
        return "cut", f"white-border bstd={bstd:.0f}"

    # isolated on pure black void (not busy scene)
    if black > 0.35 and bstd < 30 and bmean < 40:
        return "cut", f"black-field black={black:.2f}"

    return "keep", f"scene white={white:.2f} black={black:.2f} bstd={bstd:.0f}"


def asset_for_tg(tg: Path) -> Path | None:
    matches = sorted(ASSETS.glob(tg.stem + "-*.jpg"))
    return matches[0] if matches else None


def build_post_index() -> list[tuple[Path, np.ndarray]]:
    out: list[tuple[Path, np.ndarray]] = []
    for d in CONTENT.iterdir():
        if not d.is_dir():
            continue
        for name in ("fin-01.webp", "fin cover.jpg", "fin cutout.png", "img-01.webp"):
            p = d / name
            if p.exists():
                try:
                    out.append((d, fingerprint(Image.open(p))))
                except OSError:
                    pass
                break
    return out


def find_post(tg_im: Image.Image, index: list[tuple[Path, np.ndarray]]) -> Path | None:
    fp = fingerprint(tg_im)
    best: Path | None = None
    best_d = 1e9
    for post, pfp in index:
        d = fp_distance(fp, pfp)
        if d < best_d:
            best_d = d
            best = post
    # 48x48 mean abs diff; <18 is usually same image after recompress
    if best is not None and best_d < 22:
        return best
    return None


def next_cut_slug() -> str:
    n = 0
    for d in CONTENT.iterdir():
        if not d.is_dir():
            continue
        m = re.match(r"custom-cut-(\d+)$", d.name)
        if m:
            n = max(n, int(m.group(1)))
    return f"custom-cut-{n + 1:03d}"


def write_cut_post(slug: str, cut: Image.Image, original: Image.Image, title: str) -> Path:
    post = CONTENT / slug
    post.mkdir(parents=True, exist_ok=True)
    cut.save(post / "fin cutout.png")
    original.convert("RGB").save(post / "img original.jpg", quality=92)
    (post / "title.md").write_text(title + "\n", encoding="utf-8")
    (post / "tags.md").write_text("custom\ncutout\ndrop\n", encoding="utf-8")
    (post / "date.md").write_text(DATE + "\n", encoding="utf-8")
    (post / "hero.md").write_text("center\n", encoding="utf-8")
    (post / "content.md").write_text(
        "## Result\n\nSubject cut out (transparent). Original kept as resource.\n",
        encoding="utf-8",
    )
    return post


def update_existing_post(post: Path, cut: Image.Image, original: Image.Image) -> None:
    # clear prior fins so optimize picks cutout as hero
    for name in ("fin-01.webp", "fin cover.jpg", "fin cutout.png"):
        p = post / name
        if p.exists():
            p.unlink()
    cut.save(post / "fin cutout.png")
    original.convert("RGB").save(post / "img original.jpg", quality=92)
    tags = (post / "tags.md").read_text(encoding="utf-8") if (post / "tags.md").exists() else ""
    if "cutout" not in tags:
        (post / "tags.md").write_text(tags.rstrip() + "\ncutout\n", encoding="utf-8")
    content = (post / "content.md").read_text(encoding="utf-8") if (post / "content.md").exists() else ""
    if "cut out" not in content.lower():
        (post / "content.md").write_text(
            "## Result\n\nSubject cut out (transparent). Original kept as resource.\n",
            encoding="utf-8",
        )


def main() -> None:
    CUTOUTS.mkdir(parents=True, exist_ok=True)
    files = sorted(TG.glob("*.jpg"))
    cuts: list[Path] = []
    keeps = 0
    skips = 0
    for p in files:
        kind, why = classify(p)
        if kind == "cut":
            cuts.append(p)
            print("CUT?", p.name, why)
        elif kind == "skip":
            skips += 1
            print("SKIP", p.name, why)
        else:
            keeps += 1

    print(f"\nplan cut={len(cuts)} keep={keeps} skip={skips}")
    print("indexing posts…")
    index = build_post_index()
    print(f"post index {len(index)}")

    done = 0
    for src in cuts:
        print("rembg", src.name, "…")
        original = Image.open(src).convert("RGBA")
        cut = remove(original)
        cut_path = CUTOUTS / f"{src.stem}-cut.png"
        cut.save(cut_path)

        matched = find_post(original, index)
        if matched is not None:
            update_existing_post(matched, cut, original)
            print("  UPDATE", matched.name)
        else:
            slug = next_cut_slug()
            write_cut_post(slug, cut, original, f"Cutout — {src.stem}")
            print("  NEW", slug)
        done += 1

    print(f"done cutouts={done}")


if __name__ == "__main__":
    main()
