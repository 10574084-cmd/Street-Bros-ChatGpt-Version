# Street Bros — SNES Edition

A Super Mario World ROM-hack project exploring an original arcade-fighter
character and a versus-mode prototype.

## Current status

**Visual palette prototype.** The BPS patch changes the cartridge's internal
title to `STREET BROS CHATGPT` and changes the in-game player palette to a
blue-and-white outfit with a gold accent. The player is still Mario's original
silhouette and animations. There is no new playable fighter, character select,
versus mode, new map, or four-player support yet.

The next milestone is an original fighter sprite that fits Mario World's tile
layout. The project will not copy Street Fighter II's exact character sprites.

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

- Build an original player sprite that fits the existing animation/tile layout.
- Add a character-selection screen.
- Prototype one-versus-one mode.
- Evaluate whether a four-controller adapter (SNES Multitap) can be supported
  by the game's input and memory constraints.
- Expand the roster and game modes after the first playable prototype is stable.

## Project layout

- `asm/main.asm` — Asar entry point.
- `asm/features/ryu_palette.asm` — blue-and-white player palette prototype.
- `asm/features/` — future gameplay patches.
- `scripts/validate_rom.py` — verifies the expected base-ROM format.
- `.github/workflows/build-bps.yml` — assembles and packages a BPS patch.

## Important

Use a legally obtained, unmodified base ROM matching the required region and
format. Do not distribute the original game ROM. Share the patch instead.
