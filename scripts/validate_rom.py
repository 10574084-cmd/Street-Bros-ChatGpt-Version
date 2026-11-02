#!/usr/bin/env python3
"""Validate the expected clean Super Mario World USA base ROM."""
from pathlib import Path
import sys

ROM = Path(sys.argv[1] if len(sys.argv) > 1 else "Super Mario World (USA).sfc")
EXPECTED_SIZE = 512 * 1024

if not ROM.is_file():
    raise SystemExit(f"ERROR: base ROM not found: {ROM}")

size = ROM.stat().st_size
if size != EXPECTED_SIZE:
    raise SystemExit(
        f"ERROR: expected an unheadered 512 KiB SMW ROM; got {size} bytes. "
        "Check that this is the matching USA base ROM without a copier header."
    )

with ROM.open("rb") as stream:
    stream.seek(0x7FC0)
    title = stream.read(21)

if len(title) != 21:
    raise SystemExit("ERROR: could not read the SNES internal title field.")

print(f"Base ROM OK: {ROM} ({size} bytes)")
print(f"Internal title: {title.decode('ascii', errors='replace').rstrip()}")
