'!org=57344	
'!heap=768
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
#define IM2
#define DEBUG  					' This will display an error when a file is not found
#define NEX 					' We want to build into Sample.NEX
#include <nextlib.bas>			' The main library 
#include <nextlib_ints_ctc2.bas>
#include "inc-Common.bas"			' Shared between all modules 

' - Populate RAM banks for generating a NEX ------------------------------------
' These files are automatically incorporated into the final NEX and do not 
' take up memory. All modules can access these banks  
' 
' banks 24 & 25 are already assigned 
' use from bank 26 on wards 
LoadSDBank("mouse.spr",0,0,0,26)	' This is the mouse sprite in bank 26/27
LoadSDBank("aterix_font.fnt",0,0,0,28)	' This is the text font in bank 28/29
LoadSDBank("sfzii.nxt",0,0,0,29)	' This is the text font in bank 28/29
LoadSDBank("forest.pt3",0,0,0,56) 				' load music.pt3 into bank 
LoadSDBank("lemotree.pt3",0,0,0,57) 				' load music.pt3 into bank 
LoadSDBank("module3.pt3",0,0,0,58) 				' load music.pt3 into bank 
LoadSDBank("module4.pt3",0,0,0,59) 				' load music.pt3 into bank 
LoadSDBank("ts4000.bin",0,0,0,37) 				' load the music replayer into bank 
LoadSDBank("game.afb",0,0,0,38) 				' load music.pt3 into bank 
LoadSDBank("output.dat",0,0,0,60) 				' load music.pt3 into bank 
BBBREAK
asm 
	 di 							; ensure interrupts are disabled 
end asm 

InitInterupts(38,37,56)			' set up interrupts sfxbank, playerbank, music bank 
Main()							' Main call 

' Main entry

Sub Main()
	' Initialization here...
	' This is the only loop Module Control will use
	' Other modules are daisy chained from one another 
	asm 
		
		di 
		nextreg TURBO_CONTROL_NR_07,%00000011		; 28Mhz 
		nextreg SPRITE_CONTROL_NR_15,%000_000_00
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
	SetLoadModule(ModuleSample1,0,0)
	
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
		; BREAK
		ld 		(execmodule_end+1),sp 			; ensure stack is always balanced 
		call 	$6000
	execmodule_end:
		ld		sp,00000
		; di 
		
	end asm 

end sub

sub InitInterupts(byval sfxbank as ubyte, byval plbank as ubyte, byval musicbank as ubyte)
	 
	InitSFX(sfxbank)						        ' init the SFX engine, sfx are in bank 36
	InitMusic(plbank,musicbank,0000)		        ' init the music engine 33 has the player, 34 the pt3, 0000 the offset in bank 34
	SetUpCTC()							            ' init the IM2 code 
	 
	PlaySFX(3)                                    	' Plays SFX 
	EnableMusic
	EnableSFX

end sub 


ctc_sample_table:
asm 
ctc_sample_table:

	dw $3c00,0,4417 ; 0jump.pcm
	dw $3c00,4417,7516 ; 1pickup.pcm
	dw $3d00,11933-8192,7086 ; 3punch.pcm
	dw $3e00,2635,3238 ; 4dead.pcm
	dw $3e00,5873,11000 ; complete.pcm
end asm 
