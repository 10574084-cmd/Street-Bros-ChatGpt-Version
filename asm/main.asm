; Street Bros - SNES ROM hack foundation
; Base: Super Mario World (USA), unheadered 512 KiB LoROM
;
; FOUNDATION BUILD ONLY:
; This first safe test changes the internal cartridge title so the patch can
; be assembled and checked end-to-end. It does NOT add fighters or gameplay.
;
; Future gameplay patches belong in separate files under asm/features/.
lorom

; The 21-byte internal title field in the LoROM header.
org $00FFC0
db "STREET BROS CHATGPT  "
