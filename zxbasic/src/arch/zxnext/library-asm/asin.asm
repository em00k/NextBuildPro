#include once <stackf.asm>
#include once <zxnext_utils.asm>

    push namespace core

ASIN: ; Computes ASIN using ROM FP-CALC
    db $dd,01

    call        __zxnbackup_sysvar_bank

    call __FPSTACK_PUSH

    rst 28h	; ROM CALC
    defb 22h ; ASIN
    defb 38h ; END CALC

    call __FPSTACK_POP
    call __zxnbackup_sysvar_bank_restore
    ret 
    
    pop namespace

