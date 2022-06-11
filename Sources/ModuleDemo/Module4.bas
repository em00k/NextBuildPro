' ------------------------------------------------------------------------------
' - BankManager Sample v.2.0 ---------------------------------------------------
' ------------------------------------------------------------------------------
' - Sample module 4 ------------------------------------------------------------
' ------------------------------------------------------------------------------

' ORG 24576 - $6000
' Fixed bank located at $6000 to $7fff
' Usable memory from $6000 to $dd00 minus Heap size 32kB yeah
'!master=Sample.NEX
'!copy=h:\Modules\Module4.bin
'!org=24576
'!heap=2048
'!module 
'!noemu

' MARK: - Init and Main 

Init()
Main()

End 		' Exit module 


#define IM2							' we need IM2 enable for AY/CTC effects
#define NOSP
#include <nextlib.bas>				' stanbdard nextlib include 
#include <nextlib_ints_ctc2.bas>	' We're using CTC AY Effects 
#include "inc-Common.bas"			' Common routines used in all modules 
#include "inc-mouse.bas"			' mouse incldue 
#include <stRING.bas>
#include <asc.bas>


dim seg,slice,l,timer,char,abyte,bbyte,achar,bchar,mask as ubyte
dim textpos,segment,i as ubyte
dim col as ubyte
dim m$,msg$ as string

' This is the intialisation of the module 

Sub Init()
	asm 
		nextreg SPRITE_CONTROL_NR_15,%000_01001			; ensure sprites are on 
		nextreg GLOBAL_TRANSPARENCY_NR_14,0
		nextreg TRANSPARENCY_FALLBACK_COL_NR_4A,0
		ei												; ensure interrupts are on 
	end asm 
	CLS256(0)
	asm 
	nextreg	MMU2_4000_NR_52,$0a
	end asm 
	cls 
	asm 
		nextreg	MMU2_4000_NR_52,$18
	end asm 
	' PlayMusic()											' ensure music is playing on entry 
	'ShowLayer2(0)
	setscroller16(" why hello there    this is a quick test of a large scrolly             ")

end sub 

Sub Main()
	
	' Main module routine 

	dim		mouse_sfx	as ubyte = 0 
	dim		b, c, a 	as ubyte 
	dim		key 		as ubyte 
	NewMusic(59)

	' CLS256(0)
	InitSprites2(16,0,26)								' init sprites in bank 26 for mouse 
	L2Text(0,0,"MODULE 4",29,0)							' show some infos 
	L2Text(0,1,"MOUSE "+NStr(mouse_mox)+NStr(mouse_moy),29,0)
	ShowLayer2(1)
	Do 

		ProcessMouse()									' process mouse position 
		UpdatePointer()        							' updates the mouse pointer 
		WaitRetrace2(190)									' wait vblank
		asm 
			nextreg	MMU2_4000_NR_52,$0a
		end asm 
		updatescroller16()
		asm 
			nextreg	MMU2_4000_NR_52,$18
		end asm 

		if mouse_mbutt band 3 =1  						' if mouse button make an ayfx sound
			PlaySFX(mouse_sfx)			
            mouse_sfx = mouse_sfx + 1
			if mouse_sfx > 90 : mouse_sfx = 0 : enddif 
		endif 

        if mouse_mbutt band 3 =2 						' mouse button 2, start exit 
            VarLoadModule=ModuleSample1					' module to load next 
			copper_stop()								' stop copper 
			ScrollLayer(0,0)							' reset L2 position 
			reset_palette()								' reset palette to next default 
            exit do 									' exit loop 
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
			L2Text(0,7,"SAMPLE "+NStr(b),29,0)
			poke $fd3f,b
			if b < 5
				b = b + 1
			else 
				b = 1 
			endif 
			key = 1
		elseif a = code "8"	and key = 0 
			L2Text(0,8,"AY "+NStr(c),29,0)
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

	' we need to wrap any ULA stuff with restoring the ULA bank
	asm 
		nextreg	MMU2_4000_NR_52,$0a
	end asm 
	
	paper 0 : cls 
	' and on exit put back the NB8 Var banks 

	asm 
		nextreg	MMU2_4000_NR_52,$18
	end asm 
	
END SUB

sub printchar16(slice as ubyte)
		dim buffer as uinteger = 22528
		i = 1 
		forcol:
		
		for col = 0 to 7
			
			addr = @font+(cast (uinteger, char)<<5)+cast (uinteger, col)+(cast (uinteger, segment)<<4)
			
			abyte = peek(addr) << slice  band %10000000
			bbyte = peek(addr+8) << slice BAND %10000000
		
			coladd = cast(uinteger, col) << 5
			
			if abyte > 0 then 
			' print at col,31;paper 0;" "
			 poke buffer+coladd,0
			else
			
			poke buffer+coladd,i*8
			
			 'print at col,31;paper i;" "
			end if 
			coladd = cast(uinteger, col+7) << 5
			
			if bbyte > 0 then 
			 poke buffer+coladd,0
			' print at col+7,31;paper 0;" "
			else
			poke buffer+coladd,i << 4
			'print at col+7,31;paper i;" "
			end if
			
			'i = i + 1
			'if i>7
			'	i=1
			'end if
			
		next 

						
			asm 
			;di
			; halt

			ld hl,22529
			ld de,22528
			ld bc,512
			ldir
			
		end asm

	return

	
	
end sub

sub updatescroller16()

	printchar16(slice)

	slice=slice+1
		
	if slice>7
		slice=0
		segment=segment+1
		
		if segment>1
			 
			ca$=mid$(msg$,textpos,1)
			
			char = asc(ucase(msg$),textpos) : char=char-65
			if char<0 then
				char = 28
			end if 
			if ca$=" " THEN 
				char = 28
			end if 
			textpos=textpos+1
			if textpos>l-1
				textpos=1
			end if
			segment=0
		end if 
		
	end if
	return 
end sub 

sub setscroller16(m$)

	l = len(m$)
	msg$ = m$ 
	textpos=1
	slice=0
	ca$=mid$(msg$,textpos,1)
	char = asc(ucase(msg$),textpos) : char=char-65
	if char<0 then
		char =28
	end if 
	char = 28 
	
end sub 
font:
asm

	incbin "font2.bin"
end asm 