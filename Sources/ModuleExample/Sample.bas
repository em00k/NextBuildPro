'!org=57344	
'!heap=768
'#!nosys 
'!copy=H:\modules\Sample2.nex

' cp .\Sample.nex H:\modules\Sample.nex

' ORG 57344 - $E000
' Fixed bank located at $E000 to $ffff
' Usable memory from $e000 to $ffff minus heap size

' Variables are store at $4000

' ULA is paged out and banks 24/25 live in slots 2&3
' For tilemap functions the relevants pages are put back 

' - Includes -------------------------------------------------------------------
#define NOSP 					' This tells nextbuild to no set a stack pointer 
#define DEBUG  					' This will display an error when a file is not found
#define NEX 					' We want to build into Sample.NEX
#include <nextlib.bas>			' The main library 
#include "inc-common.bas"			' Shared between all modules 

' - Populate RAM banks for generating a NEX ------------------------------------
' These files are automatically incorporated into the final NEX and do not 
' take up memory. All modules can access these banks  
' 
' banks 24 & 25 are already assigned 
' use from bank 26 on wards 
LoadSDBank("testsprites.spr",0,0,0,26)	' This is the sprite in bank 26/27
LoadSDBank("font.nxt",0,0,0,28)		' This is the font, default palette is used 8x8

asm 
	di 							; ensure interrupts are disabled 
	nextreg		DISPLAY_CONTROL_NR_69,0
end asm 
paper 0 : cls 

Main()							' Main call 

' Main entry

Sub Main()
	' Initialization here...
	
	' This is the only loop Module Control will use
	' Other modules are daisy chained from one another 
	asm 
		
		di 
		nextreg TURBO_CONTROL_NR_07,%00000011		; 28Mhz 
		nextreg MMU2_4000_NR_52,24					; fresh banks		
		nextreg MMU3_6000_NR_53,25					; fresh banks 
		; wipe ram 
		ld 		hl,$4000 
		ld 		de,$4001 
		ld 		hl,(0)
		ld 		bc,$7d00 
		ldir 	
	end asm 

	' Start with module 1 
	SetLoadModule(ModuleSample2,0,0)
	
	' proceeding modules will chain 
	
MainLoop:
	
	ExecModule()
	
	if VarLoadModuleParameter2 = 9 
		' ExitToBasic()
		' Goto ExitToBasic
	endif 

	GOTO MainLoop 

END sub

ExitToBasic:
	asm 
		di 
		nextreg GLOBAL_TRANSPARENCY_NR_14,0 
		nextreg DISPLAY_CONTROL_NR_69,0				; L2 off 
		nextreg MMU2_4000_NR_52,10					; replace banks	
		nextreg MMU3_6000_NR_53,11					; replace banks 
		BREAK 
		ld 		hl,(23730)
		ld		sp,hl	
		jp		56 
	end asm 
end 

' Execute module id
sub ExecModule()

	dim file as string 
	 
	common$=NStr(VarLoadModule)					' get the module to load, NStr is a non ROM version of Str(ubyte)

	file="module"+common$(2 to )+".bin"			' combine in string 

	LoadSD(file,24576,$7d00,0)					' load from SD to $6000

	asm 
		; call the routine

		ld 		(execmodule_end+1),sp 			; ensure stack is always balanced 
		call 	$6000
	execmodule_end:
		ld		sp,0000

		
	end asm 
	
end sub

