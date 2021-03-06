; Sets ink color in ATTR_P permanently
; Parameter: Paper color in A register

#include once <sysvars.asm>
#include once <zxnext_utils.asm>

    push namespace core

INK:
    PROC
    LOCAL __SET_INK
    LOCAL __SET_INK2
    call   __zxnbackup_sysvar_bank
    ld de, ATTR_P

__SET_INK:
    cp 8
    jr nz, __SET_INK2

    inc de ; Points DE to MASK_T or MASK_P
    ld a, (de)
    or 7 ; Set bits 0,1,2 to enable transparency
    ld (de), a
    jp    __zxnbackup_sysvar_bank_restore

__SET_INK2:
    ; Another entry. This will set the ink color at location pointer by DE
    and 7	; # Gets color mod 8
    ld b, a	; Saves the color
    ld a, (de)
    and 0F8h ; Clears previous value
    or b
    ld (de), a
    inc de ; Points DE to MASK_T or MASK_P
    ld a, (de)
    and 0F8h ; Reset bits 0,1,2 sign to disable transparency
    ld (de), a ; Store new attr
    jp    __zxnbackup_sysvar_bank_restore

; Sets the INK color passed in A register in the ATTR_T variable
INK_TMP:
    ld de, ATTR_T
    call __SET_INK
    jp __zxnbackup_sysvar_bank_restore 
    ENDP

    pop namespace

