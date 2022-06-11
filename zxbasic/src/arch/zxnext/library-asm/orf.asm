#include once <u32tofreg.asm>
#include once <ftou32reg.asm>
#include once <stackf.asm>
#include once <zxnext_utils.asm>

; -------------------------------------------------------------
; Floating point library using the FP ROM Calculator (ZX 48K)

; All of them uses A EDCb registers as 1st paramter.
; For binary operators, the 2n operator must be pushed into the
; stack, in the order A DE BC.
;
; Uses CALLEE convention
; -------------------------------------------------------------

    push namespace core

__ORF:	; A | B
   ; call        __zxnbackup_sysvar_bank
    call __FPSTACK_PUSH2

    ; ------------- ROM NO-OR-NO
    rst 28h
    defb 07h	;
    defb 38h;   ; END CALC

    call __FPSTACK_POP
  ;  call  __zxnbackup_sysvar_bank_restore
    jp __FTOU8 ; Convert to 32 bits

    pop namespace

