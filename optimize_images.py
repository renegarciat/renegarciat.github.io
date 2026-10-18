#!/usr/bin/env python3
"""Batch compresses images from assets/originals/ to web-ready WebP in assets/images/.

- Reads originals from assets/originals/ (falls back to assets/images/)
- Automatically orients images based on EXIF
- Downscales to max 850px on the longest dimension
- Strips camera metadata (EXIF/GPS) for privacy and small payload
- Encodes as WebP at quality 78
- Skips images whose .webp version is already up to date
"""

import sys
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
ORIGINALS_DIR = ROOT / "assets" / "originals"
IMAGES_DIR = ROOT / "assets" / "images"

MAX_DIM = 850
QUALITY = 78


def optimize_images(force: bool = False):
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    ORIGINALS_DIR.mkdir(parents=True, exist_ok=True)

    # Search in assets/originals first, plus any loose jpg/png in assets/images
    sources = list(ORIGINALS_DIR.glob("*")) + [
        p for p in IMAGES_DIR.glob("*") if p.is_file()
    ]

    total_orig = 0
    total_opt = 0
    processed = 0
    skipped = 0

    seen = set()

    for path in sorted(sources):
        if not path.is_file():
            continue
        if path.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            continue

        base_name = path.stem
        if base_name in seen:
            continue
        seen.add(base_name)

        dest_path = IMAGES_DIR / f"{base_name}.webp"

        # Check if already optimized and newer than source
        if (
            not force
            and dest_path.exists()
            and dest_path.stat().st_mtime >= path.stat().st_mtime
        ):
            skipped += 1
            continue

        orig_size = path.stat().st_size
        total_orig += orig_size

        try:
            with Image.open(path) as img:
                img = ImageOps.exif_transpose(img)
                img.thumbnail((MAX_DIM, MAX_DIM), Image.Resampling.LANCZOS)
                # Saving without exif parameter strips all metadata
                img.save(dest_path, "WEBP", quality=QUALITY, method=6)
        except Exception as e:
            print(f"✗ Failed {path.name}: {e}")
            continue

        opt_size = dest_path.stat().st_size
        total_opt += opt_size
        processed += 1
        savings = (1 - opt_size / orig_size) * 100
        print(
            f"✓ {path.name:30} -> {dest_path.name:25} "
            f"({orig_size / 1024:>7.1f} KB -> {opt_size / 1024:>5.1f} KB, -{savings:.1f}%)"
        )

    print("-" * 75)
    if processed > 0:
        print(
            f"Optimized {processed} image(s): "
            f"{total_orig / (1024*1024):.2f} MB -> {total_opt / 1024:.1f} KB "
            f"(-{(1 - total_opt / total_orig) * 100:.1f}%)"
        )
    if skipped > 0:
        print(f"Skipped {skipped} image(s) (already up to date). Use --force to re-process.")


if __name__ == "__main__":
    force_run = "--force" in sys.argv
    optimize_images(force=force_run)
