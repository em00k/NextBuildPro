#include once <stackf.asm>
#include once <zxnext_utils.asm>

    push namespace core

TAN: ; Computes TAN using ROM FP-CALC
    call        __zxnbackup_sysvar_bank
    call __FPSTACK_PUSH

    rst 28h	; ROM CALC
    defb 21h ; TAN
    defb 38h ; END CALC

    call __FPSTACK_POP
    jp __zxnbackup_sysvar_bank_restore
    
    pop namespace

