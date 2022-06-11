' ------------------------------------------------------------------------------
' Module 1 

' ORG 24576 - $6000
' Fixed bank located at $6000 to $7fff
' Usable memory from $6000 to $dd00 minus Heap size 32kB yeah


'; We must specify the master file 
'!master=Sample.NEX				
';if you want to vopy the finalised bin
'!copy=h:\Modules\Module1.bin
'; modules always start at $6000 - 24576
'#!org=24576
'#!heap=2048
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
	for s = 0 to 64
		RemoveSprite(s,0)
	next 
end sub 

Sub Main()
	
	' Main module routine 
    CLS256(0)
	
	InitSprites2(16,0,26)								' init sprites in bank 26 for mouse 
	
	L2Text(0,0,"This is Module 1",28,0)					' show some infos 
    L2Text(0,1,"Press any key to exit module",28,0)					' show some infos 
    L2Text(0,4,"Nothing here but a blank screen",28,0)					' show some infos 
	
	Do 

		WaitRetrace(1)									' wait vblank
        if GetKey2() <> 0 
            exit do
        endif 

	Loop 

	VarLoadModule=ModuleSample2
	
end sub 
