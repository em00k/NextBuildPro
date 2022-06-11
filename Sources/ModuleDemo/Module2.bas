' ------------------------------------------------------------------------------
' - BankManager Sample v.2.0 ---------------------------------------------------
' ------------------------------------------------------------------------------
' - Sample module 2 ------------------------------------------------------------
' ------------------------------------------------------------------------------

' ORG 24576 - $6000
' Fixed bank located at $6000 to $7fff
' Usable memory from $6000 to $dd00 minus Heap size 32kB yeah
'!master=Sample.NEX
'!copy=h:\Modules\Module2.bin
'!org=24576
'#!heap=1024
'!module 



' border 3: PAPER 0 : INK 7 : CLS 
' BBREAK

Init()
Main()

'DisableIM()
End 


#define IM2
'#define NOSP 
#include <nextlib.bas>
#include <nextlib_ints_ctc2.bas>
#include "inc-Common.bas"
#include "inc-mouse.bas"

' for modules we're going to need something different that the NB7 InitMusic etc 
' Main module should initailis the IM2 and 


Sub Init()
	asm 
		nextreg SPRITE_CONTROL_NR_15,%00000011
		ei
	end asm 

	PlayMusic()
end sub 

Sub Main()
	' Show parameters
	dim	key as ubyte 
	dim b 	as ubyte
	dim c 	as ubyte
	CLS256(0) 
	
	L2Text(0,0,"MODULE 2",29,0)
	L2Text(0,1,"MOUSE "+NStr(mox)+NStr(moy),29,0)


	L2Text(0,3,"1 - STOP, 2 - PLAY",29,0)
	L2Text(0,4,"4 - TUNE 2, 5 - TUNE 1",29,0)
	
	InitSprites2(16,0,26)		' init sprites in bank 26
    
	Do 
		asm 
			nextreg TRANSPARENCY_FALLBACK_COL_NR_4A,255
		end asm 
		ProcessMouse()
		UpdatePointer()
		
		L2Text(6,0,Str(mouse_mox>>3)+NStr(mouse_moy>>3),29,1)
		L2Text(6,1,NStr(mouse_mbutt band 3),29,1)
		asm 
			nextreg TRANSPARENCY_FALLBACK_COL_NR_4A,0
		end asm 
		WaitRetrace2(1)

		if mouse_mbutt band 3 =1  
			PlaySFX(49)				' test sound fx '
            
		endif 
        if mouse_mbutt band 3 =2 
            VarLoadModule=ModuleSample3
			' BBREAK
            exit do 
        endif 

		a = GetKey2

		if a = code "1"
			StopMusic()					' stops music'
		elseif a = code "2"
			PlayMusic()					' continues music'
		elseif a = code "4"
			NewMusic(57)				' new tune in bank 56'
		elseif a = code "5"
			NewMusic(56)				' new tune in bank 57'
		elseif a = code "6"
			NewMusic(58)				' new tune in bank 57'
		elseif a = code "7"	and key = 0 
			L2Text(0,7,"SAMPLE "+NStr(b),29,200)
			poke $fd3f,b
			if b < 5
				b = b + 1
			else 
				b = 1 
			endif 
			key = 1
		elseif a = code "8"	and key = 0 
			L2Text(0,8,"AY "+NStr(c),29,200)
			PlaySFX(c)
			if c < 95
				c = c + 1
			else 
				c = 1 
			endif 
			key = 1 
		elseif a = 0 
			key = 0 
		endif 

	Loop 

END SUB



'#include "inc-copper.bas"

 