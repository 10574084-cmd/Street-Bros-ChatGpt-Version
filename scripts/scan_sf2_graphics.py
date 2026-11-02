#!/usr/bin/env python3
"""Vectorized raw 4bpp SNES tile scanner for the supplied SFII ROM."""
from __future__ import annotations
import json
import sys
import zlib
import hashlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROM = Path(sys.argv[1] if len(sys.argv) > 1 else "Super Street Fighter II (USA).sfc")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "dist/sf2-gfx")
OUT.mkdir(parents=True, exist_ok=True)
data = ROM.read_bytes()
if len(data) != 4 * 1024 * 1024:
    raise SystemExit(f"Expected 4 MiB HiROM, got {len(data)} bytes")

# The SNES 4bpp planar format stores 8x8 tiles in 32 bytes.
tiles = np.frombuffer(data, dtype=np.uint8).reshape(-1, 32)
bits = np.arange(7, -1, -1, dtype=np.uint8)[None, None, :]
p0 = (tiles[:, 0:16:2, None] >> bits) & 1
p1 = ((tiles[:, 1:16:2, None] >> bits) & 1) << 1
p2 = (tiles[:, 16:32:2, None] >> bits) & 1
p3 = ((tiles[:, 17:32:2, None] >> bits) & 1) << 1
pixels = (p0 | p1 | (p2 << 2) | (p3 << 2)).astype(np.uint8)
# pixels: [tile, y, x], 0 transparent; 1..15 grayscale indices.
palette = []
for i in range(16):
    v = 0 if i == 0 else 28 + i * 14
    palette.extend((v, v, v))
palette += [0] * (768 - len(palette))

page_w, page_h = 32*8, 64*8
overview = Image.new("RGB", (page_w*8, page_h*8), (18, 18, 18))
draw = ImageDraw.Draw(overview)
pages = []
for page in range(64):
    start = page * 2048
    page_pixels = pixels[start:start+2048].reshape(64, 32, 8, 8).transpose(0, 2, 1, 3).reshape(page_h, page_w)
    img = Image.fromarray(page_pixels, mode="P")
    img.putpalette(palette)
    px = img.convert("RGB")
    ox, oy = (page % 8)*page_w, (page // 8)*page_h
    overview.paste(px, (ox, oy))
    draw.rectangle((ox, oy, ox+90, oy+14), fill=(0, 0, 0))
    draw.text((ox+3, oy+2), f"PC {page*0x10000:06X}", fill=(255, 255, 0))
    block = tiles[start:start+2048]
    mask = np.any(block != 0, axis=1)
    coverage = float(np.count_nonzero(pixels[start:start+2048]) / (2048*64))
    pages.append({
        "offset": f"0x{page*0x10000:06X}",
        "nonblank_tiles": int(mask.sum()),
        "unique_nonblank_tiles": int(np.unique(block[mask], axis=0).shape[0]) if mask.any() else 0,
        "nonzero_pixel_ratio": round(coverage, 4),
    })
overview.save(OUT / "sf2_raw_4bpp_overview.png", optimize=True)

windows = []
for first in range(0, len(tiles), 256):
    block = tiles[first:first+256]
    mask = np.any(block != 0, axis=1)
    if not mask.any():
        continue
    unique = int(np.unique(block[mask], axis=0).shape[0])
    coverage = float(np.count_nonzero(pixels[first:first+256]) / (256*64))
    score = unique * (1.0 - abs(coverage - 0.42))
    windows.append({
        "offset": f"0x{first*32:06X}",
        "nonblank": int(mask.sum()),
        "unique": unique,
        "pixel_coverage": round(coverage, 4),
        "score": round(score, 2),
    })
windows.sort(key=lambda x: x["score"], reverse=True)
report = {
    "rom": ROM.name,
    "size": len(data),
    "crc32": f"{zlib.crc32(data) & 0xFFFFFFFF:08X}",
    "sha1": hashlib.sha1(data).hexdigest(),
    "format": "HiROM, raw 4bpp tile scan",
    "pages": pages,
    "top_windows": windows[:100],
    "note": "Heuristic candidates only; verify animation/tilemap data before using a block.",
}
(OUT / "sf2-gfx-report.json").write_text(json.dumps(report, indent=2))

# Contact sheet of the strongest 0x2000-byte candidate windows.
# Each panel is a 16x16 arrangement of raw 8x8 SNES tiles.
top = windows[:100]
panel_w, panel_h, scale = 128, 128, 2
cols, rows = 10, (len(top)+9)//10
contact = Image.new("RGB", (cols*panel_w, rows*(panel_h+18)), (20,20,20))
cdraw = ImageDraw.Draw(contact)
for n, item in enumerate(top):
    start_tile = int(item["offset"], 16)//32
    block = pixels[start_tile:start_tile+256]
    if len(block) < 256:
        continue
    panel = Image.fromarray(block.reshape(16,16,8,8).transpose(0,2,1,3).reshape(128,128), mode="P")
    panel.putpalette(palette)
    panel = panel.convert("RGB").resize((panel_w,panel_h), Image.Resampling.NEAREST)
    x, y = (n%cols)*panel_w, (n//cols)*(panel_h+18)
    contact.paste(panel, (x,y+18))
    cdraw.text((x+2,y+2), f"{item['offset']}  u{item['unique']}", fill=(255,255,0))
contact.save(OUT / "sf2-gfx-windows.png", optimize=True)

print(f"ROM CRC32: {report['crc32']}")
print(f"ROM SHA1: {report['sha1']}")
print("Top raw 4bpp candidate windows:")
for w in windows[:30]:
    print(f'{w["offset"]}: unique={w["unique"]}/256 coverage={w["pixel_coverage"]} score={w["score"]}')
print(f"Overview: {OUT/'sf2_raw_4bpp_overview.png'}")
