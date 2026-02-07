#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pillow>=10.0.0",
# ]
# ///
"""Generate a diary cover image in the same style as the Clawdi profile image.

- Uses the nano-banana-pro skill script (Gemini 3 Pro Image) to generate an image.
- Uses the existing profile image as a style reference.
- Post-processes to 16:9 (center crop) and saves PNG.

Usage:
  python3 scripts/generate_diary_cover.py --date 2026-02-07 --title "..." --summary "..." \
    --out assets/diary-covers/2026-02-07.png
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
NB_SCRIPT = Path("/home/clawdi/.npm-global/lib/node_modules/openclaw/skills/nano-banana-pro/scripts/generate_image.py")
STYLE_REF = ROOT / "assets" / "clawdi-profile.jpg"


def center_crop_to_16_9(img: Image.Image, target_width: int | None = None) -> Image.Image:
    # Ensure RGB
    if img.mode != "RGB":
        img = img.convert("RGB")

    w, h = img.size
    target_ratio = 16 / 9
    current_ratio = w / h

    if abs(current_ratio - target_ratio) < 1e-3:
        cropped = img
    elif current_ratio > target_ratio:
        # Too wide -> crop width
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        cropped = img.crop((left, 0, left + new_w, h))
    else:
        # Too tall -> crop height
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        cropped = img.crop((0, top, w, top + new_h))

    if target_width:
        target_height = int(target_width * 9 / 16)
        cropped = cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)

    return cropped


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--title", required=True)
    ap.add_argument("--summary", required=True, help="Short summary of the day to guide the image")
    ap.add_argument("--out", required=True, help="Output path (PNG)")
    ap.add_argument("--resolution", default="1K", choices=["1K", "2K", "4K"])
    ap.add_argument("--width", type=int, default=1280, help="Final width for 16:9 output")
    args = ap.parse_args()

    if not NB_SCRIPT.exists():
        raise SystemExit(f"Nano banana script not found: {NB_SCRIPT}")
    if not STYLE_REF.exists():
        raise SystemExit(f"Style reference image missing: {STYLE_REF}")

    out_path = (ROOT / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = out_path.with_suffix(".tmp.png")

    prompt = (
        "Create a cozy 1990s pixel-art diary cover illustration in the exact same style as the reference image. "
        "Scene should feel like a warm nerdy home office: bookshelves, anime/game vibe, cables, desk, CRT monitor. "
        "Add subtle visual hints about today's diary entry. "
        f"Date: {args.date}. Title: {args.title}. Context hints: {args.summary}. "
        "No readable text in the image. Cinematic lighting, soft gradients, crisp pixel style."
    )

    cmd = [
        "uv",
        "run",
        str(NB_SCRIPT),
        "--prompt",
        prompt,
        "--filename",
        str(tmp_path),
        "--resolution",
        args.resolution,
        "-i",
        str(STYLE_REF),
    ]

    # Run from repo root so uv can work anywhere
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    if proc.returncode != 0:
        # Fallback: if image generation fails (e.g., quota), create a 16:9 crop of the profile image
        # so the diary entry still looks good.
        print("Image generation failed; using fallback cover (cropped profile image).")
        print(proc.stdout)
        print(proc.stderr)
        img = Image.open(STYLE_REF)
        final = center_crop_to_16_9(img, target_width=args.width)
        final.save(out_path, "PNG")
        print(f"Saved fallback cover: {out_path}")
        print(f"MEDIA: {out_path}")
        return 0

    # Postprocess
    img = Image.open(tmp_path)
    final = center_crop_to_16_9(img, target_width=args.width)
    final.save(out_path, "PNG")

    # Cleanup
    try:
        tmp_path.unlink()
    except Exception:
        pass

    print(f"Saved cover: {out_path}")
    print(f"MEDIA: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
