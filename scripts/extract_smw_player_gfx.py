#!/usr/bin/env python3
"""Extract Super Mario World's compressed player graphics for layout study."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROM = Path(sys.argv[1] if len(sys.argv) > 1 else "Super Mario World (USA).sfc")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "dist/smw-player-gfx")
OUT.mkdir(parents=True, exist_ok=True)
rom = ROM.read_bytes()
if len(rom) != 0x80000:
    raise SystemExit(f"Expected 512 KiB SMW USA ROM, got {len(rom)} bytes")

def decompress_lc_lz2(src: bytes, limit: int = 0x20000) -> bytes:
    out = bytearray()
    i = 0
    while i < len(src):
        command = src[i]
        i += 1
        if command == 0xFF:
            return bytes(out)
        if command >> 5 == 7:
            if i >= len(src):
                raise ValueError("Truncated extended LC_LZ2 command")
            size = ((command & 3) << 8) | src[i]
            size += 1
            mode = (command & 0x1C) >> 2
            i += 1
        else:
            size = (command & 0x1F) + 1
            mode = command >> 5
        if mode == 0:
            out.extend(src[i:i+size])
            i += size
        elif mode == 1:
            value = src[i]
            i += 1
            out.extend([value] * size)
        elif mode == 2:
            a, b = src[i], src[i+1]
            i += 2
            for n in range(size):
                out.append(a if (n & 1) == 0 else b)
        elif mode == 3:
            value = src[i]
            i += 1
            out.extend((value+n) & 0xFF for n in range(size))
        elif mode == 4:
            pos = (src[i] << 8) | src[i+1]
            i += 2
            for n in range(size):
                if pos+n >= len(out):
                    raise ValueError("LC_LZ2 back-reference outside output")
                out.append(out[pos+n])
        else:
            raise ValueError(f"Unsupported LC_LZ2 mode {mode} at source {i:#x}")
        if len(out) > limit:
            raise ValueError("LC_LZ2 output exceeded safety limit")
        if i > len(src):
            raise ValueError("LC_LZ2 command overran source")
    raise ValueError("No LC_LZ2 terminator found")

def decode_4bpp(tile: bytes) -> bytes:
    px = bytearray(64)
    for y in range(8):
        p0, p1 = tile[2*y], tile[2*y+1]
        p2, p3 = tile[16+2*y], tile[17+2*y]
        for x in range(8):
            bit = 7-x
            px[y*8+x] = ((p0>>bit)&1) | (((p1>>bit)&1)<<1) | (((p2>>bit)&1)<<2) | (((p3>>bit)&1)<<3)
    return bytes(px)

compressed_offset = 0x40000
compressed_length = 0x3FC0
gfx = decompress_lc_lz2(rom[compressed_offset:compressed_offset+compressed_length])
if len(gfx) % 32:
    raise SystemExit(f"Decompressed graphics size is not tile aligned: {len(gfx)}")
count = len(gfx)//32
cols = 32
rows = (count+cols-1)//cols
sheet = Image.new("RGB", (cols*8*4, rows*8*4), (24,24,24))
draw = ImageDraw.Draw(sheet)
# Neutral grayscale index palette for tile structure inspection.
colors = [(0,0,0)] + [(i*16, i*16, i*16) for i in range(1,16)]
for idx in range(count):
    tile = decode_4bpp(gfx[idx*32:(idx+1)*32])
    x, y = (idx%cols)*32, (idx//cols)*32
    im = Image.new("RGB",(8,8))
    im.putdata([colors[v] for v in tile])
    im = im.resize((32,32), Image.Resampling.NEAREST)
    sheet.paste(im,(x,y))
    if idx%16 == 0:
        draw.text((x,y),f"{idx:03X}",fill=(255,255,0),stroke_width=1,stroke_fill=(0,0,0))
sheet.save(OUT/"smw-player-tiles.png", optimize=True)
(OUT/"player-gfx.bin").write_bytes(gfx)
(OUT/"report.json").write_text(json.dumps({
    "rom":ROM.name,"compressed_offset":hex(compressed_offset),
    "compressed_size":compressed_length,"decompressed_size":len(gfx),
    "tile_count":count,"sheet":"smw-player-tiles.png",
},indent=2))
print(f"Compressed range: {compressed_offset:#x}..{compressed_offset+compressed_length:#x}")
print(f"Decompressed player graphics: {len(gfx)} bytes ({count} tiles)")
print(f"Preview: {OUT/'smw-player-tiles.png'}")
