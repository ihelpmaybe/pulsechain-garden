"""One-shot: add a dump of images as garden posts (optional rembg cutouts)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image
from rembg import remove

GARDEN = Path(__file__).resolve().parents[1]
ASSETS = Path(r"C:\Users\punki\.cursor\projects\c-Users-punki-Desktop-windows-clone\assets")

BATCH = [
    ("custom-sv-groyper-room-1", "photo_2_2026-11-25_20-30-13-2532a350-3083-4c09-94cd-5526d957a4fc.jpg",
     "Sailor Venus + HEX frog room", "custom\nsailor-venus\nmascot\npepe", False),
    ("custom-sv-rh-reflection-1", "photo_10_2026-11-25_20-30-13-278b716e-66d2-4284-954e-daa3ab97ce34.jpg",
     "Sailor Venus / RH mirror squat", "custom\nsailor-venus\nrichard-heart\nmeme", False),
    ("custom-sv-reaction-meme-1", "photo_12_2026-11-25_20-30-13-bcefc891-08da-4d9a-8c23-d178fc3bca89.jpg",
     "Sailor Venus reaction meme", "custom\nsailor-venus\nmeme", False),
    ("custom-sv-ambulance-rpg-1", "photo_13_2026-11-25_20-30-13-bb0f2ae4-3746-4477-b30f-cbf32059d68e.jpg",
     "Sailor Venus — call an ambulance", "custom\nsailor-venus\nmeme", False),
    ("custom-sv-grimace-selfie-1", "photo_3_2026-11-25_20-30-13-9681dacb-007c-41f4-a507-a8617a8b338a.jpg",
     "Sailor Venus cosplay grimace", "custom\nsailor-venus\ncutout\ncosplay", True),
    ("custom-sv-kanye-1", "photo_8_2026-11-25_20-30-13-dd279d23-212b-45a9-beab-8ea359b6ed72.jpg",
     "Sailor Venus + Ye", "custom\nsailor-venus\nmeme", False),
    ("custom-jesse-shitcoin-1", "photo_9_2026-11-25_20-30-13-a9741c86-18ff-4f8b-9766-f49827428209.jpg",
     "Whos the shitcoin now", "custom\nmeme\npulsechain", False),
    ("custom-sv-simp-1", "photo_7_2026-11-25_20-30-13-f6f1a4a1-98d0-4901-a16f-fa33f9510c44.jpg",
     "Sailor Venus — Simp", "custom\nsailor-venus\nmeme\ncutout", True),
    ("custom-sv-hex-shield-1", "photo_1_2026-11-25_20-30-13-382e3a0a-f9ce-4156-9478-b547aedfed6b.jpg",
     "Sailor Venus HEX shield cosplay", "custom\nsailor-venus\nhex\ncutout\ncosplay", True),
    ("custom-hex-priestess-1", "photo_14_2026-11-25_20-30-13-3ac3057b-2205-4343-b657-dee55884f0dd.jpg",
     "HEX priestess — blessing", "custom\nhex\nsailor-venus\ncutout", True),
    ("custom-rh-prison-suit-1", "photo_5_2026-11-25_20-30-13-c4c6658a-18f7-4340-809b-410ed6594799.jpg",
     "RH prison tracksuit 5555369", "custom\nrichard-heart\nhex\ncutout", True),
    ("custom-rh-lv-suit-1", "photo_4_2026-11-25_20-30-13-7d39e9b6-aacb-498c-94e5-294eaf63066b.jpg",
     "RH LV tracksuit + HEX chain", "custom\nrichard-heart\nhex\ncutout", True),
    ("custom-hex-nascar-1", "photo_6_2026-11-25_20-30-13-37a8b56b-c02d-4f25-bc43-9090494fe8a6.jpg",
     "HEX.com NASCAR 55", "custom\nhex\nracing", False),
    ("custom-sv-hex-halloween-1", "photo_11_2026-11-25_20-30-13-99014c33-e20d-4502-b382-0930cb8b27a0.jpg",
     "HEX Happy Halloween Sailor Venus", "custom\nsailor-venus\nhex\nhalloween", False),
]


def main() -> None:
    batch_dir = GARDEN / "data" / "batch"
    batch_dir.mkdir(parents=True, exist_ok=True)
    for slug, filename, title, tags, do_cut in BATCH:
        src = ASSETS / filename
        if not src.exists():
            print("MISSING", filename)
            continue
        post = GARDEN / "content" / slug
        post.mkdir(parents=True, exist_ok=True)
        im = Image.open(src).convert("RGBA")
        if do_cut:
            result = remove(im)
            result.save(post / "fin cutout.png")
            im.convert("RGB").save(post / "img original.jpg", quality=92)
            result.save(batch_dir / f"fin-{slug}.png")
            print("CUT", slug)
        else:
            im.convert("RGB").save(post / "fin cover.jpg", quality=92)
            print("ADD", slug)
        (post / "title.md").write_text(title + "\n", encoding="utf-8")
        (post / "tags.md").write_text(tags.strip() + "\n", encoding="utf-8")
        (post / "date.md").write_text("2026-11-25\n", encoding="utf-8")
        (post / "hero.md").write_text("center\n", encoding="utf-8")
        (post / "content.md").write_text("## Result\n\nBatch drop for PulseChain Garden.\n", encoding="utf-8")
    print("batch done", len(BATCH))


if __name__ == "__main__":
    main()
