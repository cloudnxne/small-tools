#!/usr/bin/env python3
"""
Convert images to WebP.

Handles PNG, JPG/JPEG, BMP, TIFF and GIF by default.

Usage:
    python img_to_webp.py                        # converts supported images in the current folder
    python img_to_webp.py /path/to/folder        # converts supported images in a given folder
    python img_to_webp.py --quality 90           # set WebP quality (default 80)
    python img_to_webp.py --types png,jpg,gif    # restrict to specific extensions
    python img_to_webp.py --recursive            # also convert images in subfolders
    python img_to_webp.py --delete-original      # delete the source files after conversion

Requires Pillow:
    pip install Pillow
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is not installed. Run: pip install Pillow")

DEFAULT_EXTENSIONS = ["png", "jpg", "jpeg", "bmp", "tiff", "tif", "gif"]


def find_images(folder: Path, extensions: list[str], recursive: bool) -> list[Path]:
    pattern = "**/*" if recursive else "*"
    files = []
    for ext in extensions:
        files.extend(folder.glob(f"{pattern}.{ext}"))
        files.extend(folder.glob(f"{pattern}.{ext.upper()}"))
    return sorted(set(files))


def convert_folder(folder: Path, extensions: list[str], quality: int, recursive: bool, delete_originals: bool) -> None:
    images = find_images(folder, extensions, recursive)

    if not images:
        print(f"No matching image files found in {folder}")
        return

    print(f"Found {len(images)} image file(s) in {folder}\n")

    converted = 0
    failed = 0

    for img_path in images:
        webp_path = img_path.with_suffix(".webp")
        try:
            with Image.open(img_path) as img:
                # Animated GIFs: preserve animation
                if getattr(img, "is_animated", False):
                    img.save(webp_path, "webp", quality=quality, save_all=True)
                else:
                    if img.mode in ("P", "RGBA") and img.format != "PNG":
                        img = img.convert("RGBA")
                    img.save(webp_path, "webp", quality=quality)
            print(f"  {img_path.name} -> {webp_path.name}")
            converted += 1

            if delete_originals:
                img_path.unlink()

        except Exception as e:
            print(f"  Failed on {img_path.name}: {e}")
            failed += 1

    print(f"\nDone. Converted {converted} file(s)." + (f" {failed} failed." if failed else ""))


def main():
    parser = argparse.ArgumentParser(description="Convert images to WebP.")
    parser.add_argument("folder", nargs="?", default=".", help="Folder containing images (default: current folder)")
    parser.add_argument("--quality", type=int, default=80, help="WebP quality, 0-100 (default: 80)")
    parser.add_argument(
        "--types",
        default=",".join(DEFAULT_EXTENSIONS),
        help=f"Comma-separated list of extensions to convert (default: {','.join(DEFAULT_EXTENSIONS)})",
    )
    parser.add_argument("--recursive", action="store_true", help="Also convert images in subfolders")
    parser.add_argument("--delete-original", action="store_true", help="Delete original files after conversion")
    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        sys.exit(f"Not a valid folder: {folder}")

    extensions = [e.strip().lstrip(".").lower() for e in args.types.split(",") if e.strip()]

    convert_folder(folder, extensions, args.quality, args.recursive, args.delete_original)


if __name__ == "__main__":
    main()
