' ------------------------------------------------------------------------------
' Module 1 

' ORG 24576 - $6000
' Fixed bank located at $6000 to $7fff
' Usable memory from $6000 to $dd00 minus Heap size 32kB yeah


'; We must specify the master file 
'!master=Sample.NEX				
';if you want to vopy the finalised bin
'!copy=h:\Modules\Module4.bin
'; modules always start at $6000 - 24576
'!org=24576
'!heap=2048
'!module 
'!noemu

' MARK: - Init and Main 

Init()
Main()

End 		' Exit module 

#include <nextlib.bas>				' stanbdard nextlib include 
#include "inc-common.bas"			' Common routines used in all modules 

' This is the intialisation of the module 

Sub Init()
	asm 
		nextreg SPRITE_CONTROL_NR_15,%00000011			; ensure sprites are on 
	end asm 
end sub 

Sub Main()
	
	' Main module routine 

	InitSprites2(16,0,26)								' init sprites in bank 26 for mouse 
	L2Text(0,0,"MODULE 4",29,0)							' show some infos 
	L2Text(0,1,"MOUSE "+NStr(mox)+NStr(moy),29,0)

	Do 

		ProcessMouse()									' process mouse position 
		UpdatePointer()        							' updates the mouse pointer 
		WaitRetrace(1)									' wait vblank

	Loop 

END SUB
