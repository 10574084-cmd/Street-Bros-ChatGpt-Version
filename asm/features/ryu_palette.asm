; Original arcade-fighter palette prototype for the existing player sprite.
; Blue-and-white outfit with a gold accent. This changes colors only; it does
; not copy Street Fighter character graphics or change the game's move logic.

; Normal player palette, 10 SNES BGR555 colors in little-endian order.
; Keep the first skin tone; replace the main red/dark-red clothing colors.
org $00B2C8
db $5F,$63  ; skin tone / highlight (retained)
db $00,$7C  ; deep blue
db $00,$40  ; navy shadow
db $FF,$7F  ; white cloth
db $E0,$7F  ; light cyan cloth highlight
db $10,$40  ; dark blue detail
db $FF,$7F  ; white accent
db $FF,$03  ; gold sash detail
db $1F,$00  ; warm red accent
db $FF,$03  ; gold highlight

; Overworld player palette (two colors).
org $00B59C
db $00,$7C,$FF,$7F
