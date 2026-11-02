; Ryu-inspired color prototype for the existing player sprite.
; This is a palette edit only: it does not replace Mario's graphics or moves.
;
; SMW's normal player palette is stored at PC $0032C8 (LoROM $00:B2C8).
; The overworld player palette is stored at PC $00359C (LoROM $00:B59C).
;
; Colors below are SNES BGR555 little-endian values.
; Keep skin/shadow colors mostly intact; switch the main clothing colors to
; white and blue, with a red accent.

; In-level normal Mario palette (20 bytes).
org $00B2C8
db $5F,$63  ; skin highlight
db $1D,$58  ; dark red accent
db $0A,$00  ; darkest shade
db $9B,$7B  ; gi cloth: off-white
db $E3,$5C  ; gi shadow: deep blue
db $08,$7E  ; gi highlight: bright blue
db $70,$67  ; retained midtone
db $32,$08  ; dark red detail
db $7F,$10  ; red headband accent
db $FF,$03  ; retained yellow detail

; Overworld player palette (two colors).
org $00B59C
db $E3,$5C,$08,$7E
