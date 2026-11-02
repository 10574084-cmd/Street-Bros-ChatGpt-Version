# Street Bros — SNES Edition

A Super Mario World ROM-hack project exploring a Street Fighter-inspired
character-select and versus experience.

## Current status

**Foundation build only.** The repository now has an Asar + Floating IPS build
pipeline. The first test patch changes the SNES internal cartridge title to
`STREET BROS CHATGPT`, proving the assembler-to-BPS pipeline. It does not
yet add playable fighters, versus mode, new maps, or four-player support.

## Build

1. Keep a clean, unheadered **Super Mario World (USA)** base ROM at:
   `Super Mario World (USA).sfc`
2. Open the repository's **Actions** tab.
3. Run **Build Street Bros BPS** with **Run workflow** (or push a change to
   `asm/**`, `scripts/**`, or the workflow).
4. Download the `Street-Bros-BPS` artifact from the completed run.

The artifact is a **BPS patch**, not a game ROM. Apply it only to a clean,
matching copy of the base game. The build checks the base ROM size and emits
the patch plus build metadata.

## Planned development

- Inspect the original game routines and map data before changing gameplay.
- Add a character-selection screen and original fighter graphics.
- Prototype one-versus-one mode.
- Evaluate whether a four-controller adapter (SNES Multitap) can be supported
  by the game's input and memory constraints.
- Expand the roster and special-move logic only after the first playable
  prototype is stable.

## Project layout

- `asm/main.asm` — Asar entry point.
- `asm/features/ryu_palette.asm` — first in-game palette prototype.
- `asm/features/` — future gameplay patches.
- `scripts/validate_rom.py` — verifies the expected base-ROM format.
- `.github/workflows/build-bps.yml` — assembles and packages a BPS patch.

## Important

Use a legally obtained, unmodified base ROM matching the required region and
format. Do not distribute the original game ROM. Share the patch instead.
