#!/usr/bin/env python3
"""Build an indexed contact sheet of raw SNES 4bpp tile candidates.

This is an analysis aid only. It does not claim that every scanned block is
character art; tables, code and compressed streams will appear as noise.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from collections import Counter

try:
    from PIL import Image, ImageDraw
except ImportError as exc:
    raise SystemExit("Install Pillow: python -m pip install pillow") from exc

ROM = Path(sys.argv[1] if len(sys.argv) > 1 else "Super Street Fighter II (USA).sfc")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "dist/sf2-gfx")
OUT.mkdir(parents=True, exist_ok=True)
data = ROM.read_bytes()
if len(data) != 4 * 1024 * 1024:
    raise SystemExit(f"Expected 4 MiB HiROM, got {len(data)} bytes")

# SNES 4bpp planar tile decoder (8x8 pixels, 32 bytes).
def decode_tile(src: bytes) -> list[int]:
    px = [0] * 64
    for y in range(8):
        p0, p1 = src[2*y], src[2*y+1]
        p2, p3 = src[16+2*y], src[17+2*y]
        for x in range(8):
            bit = 7 - x
            px[y*8+x] = (((p0 >> bit) & 1)
                         | (((p1 >> bit) & 1) << 1)
                         | (((p2 >> bit) & 1) << 2)
                         | (((p3 >> bit) & 1) << 3))
    return px

# Use a simple grayscale index ramp so tile silhouettes are visible without
# guessing character CGRAM palettes.
palette = []
for i in range(16):
    v = 0 if i == 0 else 36 + i * 13
    palette.extend((v, v, v))
palette += [0] * (768 - len(palette))

# 64 pages; each page covers 0x10000 bytes = 2048 tiles, arranged 32x64.
page_w, page_h = 32*8, 64*8
overview = Image.new("RGB", (page_w*8, page_h*8), (24, 24, 24))
draw = ImageDraw.Draw(overview)
stats = []

for page in range(64):
    start = page * 0x10000
    block = data[start:start+0x10000]
    tiles = [block[i:i+32] for i in range(0, len(block), 32)]
    img = Image.new("P", (page_w, page_h), 0)
    img.putpalette(palette)
    nonblank = 0
    unique = set()
    px_nonzero = 0
    for idx, t in enumerate(tiles):
        if len(t) != 32:
            continue
        raw = bytes(t)
        if any(raw):
            nonblank += 1
            unique.add(raw)
        pix = decode_tile(raw)
        px_nonzero += sum(1 for v in pix if v)
        x = (idx % 32) * 8
        y = (idx // 32) * 8
        img.putdata([]) if False else None
        # Paste the tile into the page image using a tiny indexed tile.
        tile_img = Image.frombytes("P", (8, 8), bytes(pix))
        tile_img.putpalette(palette)
        img.paste(tile_img, (x, y))
    # Label each page with its exact ROM offset in the aggregate overview.
    page_rgb = img.convert("RGB")
    ox, oy = (page % 8)*page_w, (page // 8)*page_h
    overview.paste(page_rgb, (ox, oy))
    draw.rectangle((ox, oy, ox+85, oy+14), fill=(0,0,0))
    draw.text((ox+3, oy+2), f"PC {start:06X}", fill=(255,255,0))
    stats.append({
        "offset": f"0x{start:06X}",
        "nonblank_tiles": nonblank,
        "unique_nonblank_tiles": len(unique),
        "nonzero_pixel_ratio": round(px_nonzero/(len(tiles)*64), 4),
    })

overview.save(OUT / "sf2_raw_4bpp_overview.png", optimize=True)

# Fine-grained 0x2000-byte window metrics for candidate ranking.
windows = []
for start in range(0, len(data), 0x2000):
    block = data[start:start+0x2000]
    tiles = [block[i:i+32] for i in range(0, len(block), 32)]
    nonblank = [t for t in tiles if any(t)]
    if not nonblank:
        continue
    unique = len(set(nonblank))
    nonzero = sum(sum(decode_tile(t)[i] != 0 for i in range(64)) for t in nonblank)
    denom = max(1, len(nonblank)*64)
    # Prefer many unique tiles and a mixture of transparent/opaque pixels.
    ratio = nonzero/denom
    score = unique * (1.0 - abs(ratio - 0.42))
    windows.append({
        "offset": f"0x{start:06X}",
        "nonblank": len(nonblank),
        "unique": unique,
        "pixel_coverage": round(ratio, 4),
        "score": round(score, 2),
    })
windows.sort(key=lambda x: x["score"], reverse=True)
report = {
    "rom": ROM.name,
    "size": len(data),
    "format": "HiROM, raw 4bpp tile scan",
    "pages": stats,
    "top_windows": windows[:100],
    "note": "Candidates are heuristic only; confirm tiles in context before using them."
}
(OUT / "sf2-gfx-report.json").write_text(json.dumps(report, indent=2))
print("Top raw 4bpp candidate windows:")
for w in windows[:30]:
    print(f'{w["offset"]}: unique={w["unique"]}/256 coverage={w["pixel_coverage"]} score={w["score"]}')
print(f"Overview: {OUT/'sf2_raw_4bpp_overview.png'}")
