#include once <u32tofreg.asm>
#include once <ftou32reg.asm>
#include once <stackf.asm>
#include once <zxnext_utils.asm>
; -------------------------------------------------------------
; Floating point library using the FP ROM Calculator (ZX 48K)

; All of them uses C EDHL registers as 1st paramter.
; For binary operators, the 2n operator must be pushed into the
; stack, in the order BC DE HL (B not used).
;
; Uses CALLEE convention
; -------------------------------------------------------------

    push namespace core

__NEGF:	; A = -A
    ;call        __zxnbackup_sysvar_bank
    call __FPSTACK_PUSH

    ; ------------- ROM NEGATE
    rst 28h
    defb 1Bh	; NEGF
    defb 38h;   ; END CALC

    jp __FPSTACK_POP
    ;jp __zxnbackup_sysvar_bank_restore

    pop namespace


