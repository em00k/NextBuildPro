' ----------------------------------------------------------------
' This file is released under the MIT License
' 
' Copyleft (k) 2008
' by Jose Rodriguez-Rosa (a.k.a. Boriel) <http://www.boriel.com>
' ----------------------------------------------------------------

#ifndef __LIBRARY_POINT__

REM Avoid recursive / multiple inclusion

#define __LIBRARY_POINT__

#pragma push(case_insensitive)
#pragma case_insensitive = TRUE

' ----------------------------------------------------------------
' function POINT(x, y)
' 
' Parameters: 
'     x: X coord (0 to 255) 
'     y: Y coord (0 to 191)
'
' Returns:
'     1 if point is plot 0 otherwise (byte)
' ----------------------------------------------------------------
function fastcall point(x as ubyte, y as ubyte) as byte
	asm

	PROC
	LOCAL PIXEL_ADDR
	LOCAL POINT_LOOP
	LOCAL POINT_END
    LOCAL POINT_1

PIXEL_ADDR EQU (22AAh + 6)	; ROM addrs which calculate screen addr

    pop hl
    ex (sp), hl  ; callee => put RET address back. H = y
	ld b, h
	ld c, a

#ifdef SCREEN_Y_OFFSET
    ld a, SCREEN_Y_OFFSET
    add a, b
    ld b, a
#endif

#ifdef SCREEN_X_OFFSET
    ld a, SCREEN_X_OFFSET
    add a, c
    ld c, a
#endif

	ld a, 191 ; Max y value
	sub b	
	jp nc, POINT_1	  ; Error checking here

	ld a, -1
	jr POINT_END

POINT_1:
	call PIXEL_ADDR

	; Ripped from the ZX ROM

	ld b, a    ; pixel position to B, 0-7.
	inc b      ; increment to give rotation count 1-8.
	ld a, (hl) ; fetch byte from screen.

POINT_LOOP:
	rlca	   ; rotate and loop back
	djnz POINT_LOOP ; to POINT-LP until pixel at right.
	and 1      ; test to give zero or one.

POINT_END:
	ENDP

	end asm
end function

#pragma pop(case_insensitive)


#endif

