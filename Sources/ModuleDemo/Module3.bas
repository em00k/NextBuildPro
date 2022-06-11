' ------------------------------------------------------------------------------
' - BankManager Sample v.2.0 ---------------------------------------------------
' ------------------------------------------------------------------------------
' - Sample module 3 ------------------------------------------------------------
' ------------------------------------------------------------------------------

' ORG 24576 - $6000
' Fixed bank located at $6000 to $7fff
' Usable memory from $6000 to $dd00 minus Heap size 32kB yeah
'!master=Sample.NEX
'!copy=h:\Modules\Module3.bin
'!org=24576
'!heap=512
'!module 
'!noemu

dim co(255) as byte 
dim si(255) as byte 
'Dim R, R2,  D2, XA, YA, YT,L as integer
dim C as uinteger
dim offset as integer 
dim ca,cb,lp as byte 
dim Color, cc,nc, W, H,rx,X, Y,value,XX,YY,u,v,o,p,a,b,XO,YO,t,r as ubyte 
dim kx as integer

' border 3: PAPER 0 : INK 7 : CLS 
' BBREAK

Init()
Main()

'DisableIM()
End 


#define IM2
#define NOSP 
#include <nextlib.bas>
#include <nextlib_ints_ctc2.bas>
#include "inc-Common.bas"
#include "inc-mouse.bas"

' for modules we're going to need something different that the NB7 InitMusic etc 
' Main module should initailis the IM2 and 
function dist(byval dista as integer,byval distb as integer,byval distc as integer,byval distd as integer) as ubyte
C=(((dista - distc) * (dista - distc)) + ((distb - distd) * (distb - distd)))
asm 
    ;BREAK 
    ; use John Metcalfs fast sqr 
    ; http://www.retroprogramming.com/2017/07/a-fast-z80-integer-square-root.html
    fastsqr: ld a,h : 	ld de,0B0C0h : 	add a,e : jr c,sq7 : ld a,h : 	ld d,0F0h
    sq7: add a,d : jr nc,sq6 : res 5,d : db 254 
    sq6: sub d : sra d : set 2,d : add a,d : jr nc,sq5 : res 3,d : db 254 
    sq5: sub d : sra d : inc d : add a,d : jr nc,sq4 : res 1,d : db 254 
    sq4: sub d : sra d : ld h,a : add hl,de : jr nc,sq3 : ld e,040h : db 210
    sq3: sbc hl,de : sra d : ld a,e : rra : or 010h : ld e,a : add hl,de : jr nc,sq2 : and 0DFh : db 218 
    sq2: sbc hl,de : sra d : rra : or 04h : ld e,a : add hl,de : jr nc,sq1 : and 0F7h : db 218
    sq1: sbc hl,de : sra d : rra : inc a : ld e,a : add hl,de : jr nc,sq0 : and 0FDh
    sq0: sra d : rra : cpl : ld hl,0 : ADD_HL_A : ld (._C),a
END ASM 
    Return C
end function

Sub Init()
	asm 
		nextreg SPRITE_CONTROL_NR_15,%00000011
		ei
	end asm 


end sub 

Sub Main()
	' Show parameters
	dim	key as ubyte 
	dim b 	as ubyte
	dim c 	as ubyte
	dim R 	as ubyte
	dim R2 	as ubyte

	NewMusic(58)			
	
    asm 
        nextreg PALETTE_CONTROL_NR_43,%0_001_0000
    end asm 
    PalUpload(@rainbow, 0,16)

    
    ' paper 0 : ink 6: border 0 : cls
    'CLS256(0) : ShowLayer2(1) 
    'pause 0

    nc = 0 : offset = 16
    R = 127 : R2 = R * R : H = 192 : W = 255
    ClipLayer2(0,255,48,128)
	lp = 0 
    do '' 6.28*4 step 0.05
    
     co(rx) = (int(16*(fCos(kx))))
     si(rx) = (int(4*fSin(kx))) 
    ' print co(rx),si(rx)   ',ZA	
     rx = rx + 1
    kx = kx + 3
     ' 6.28*4 : endif 
	 lp = lp + 1 
    loop until lp = 0
    rx=0 : XO =0 
    X=0
    do 
            
                    For Y = 0 To H-1
                        ca=(co(X))-si(Y) : 
                        C=cast(uinteger,ca) : C = C - ( cast(uinteger,(  Y)) ) : 
                        Color = cast(ubyte,(C  ) )  
                        
                        PlotL2(cast(ubyte,(X)),cast(ubyte,(Y)),Color)
    
                        'YO=YO+1' : if YO>191 : YO = 0 : ENDIF 
            Next
                    'XO=XO+1 ': if XO>126 : XO = 0 : ENDIF 		
		X = X + 1
    loop until X = 0 
     
	
	InitSprites2(16,0,26)		' init sprites in bank 26
	L2Text(0,0,"MODULE 3",29,0)
	L2Text(0,1,"MOUSE "+NStr(mouse_mox)+NStr(mouse_moy),29,0)


	L2Text(0,3,"1 - STOP, 2 - PLAY",29,0)
	L2Text(0,4,"4 - TUNE 2, 5 - TUNE 1",29,0)

	Do 
		asm 
			nextreg TRANSPARENCY_FALLBACK_COL_NR_4A,0
		end asm 
		ProcessMouse()
		UpdatePointer()
       
        'NextReg($40,0) : NextReg($44,0) : NextReg($44,0)
        'if b>2 : 
        cb=cb-2 ': else : b = 254 : endif 
        cc=cc+1 ': b=b-2 : if b = 0 : b = 254 : endif 
        if cc=255
            if nc = 16
            '	nc = 32
            elseif nc = 32
            '	nc = 16
            'elseif nc = 42
            '	nc = 16
            endif 
        endif 
         
		WaitRetrace(1)

		if mouse_mbutt band 3 =1  
			PlaySFX(49)				' test sound fx '
            
		endif 
        if mouse_mbutt band 3 =2 
            VarLoadModule=ModuleSample4
			' BBREAK
			copper_stop()
			ScrollLayer(0,0)
			reset_palette()
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
		
		PalUpload(@rainbow, nc,cb)

		asm 
			call _copper_wobble
		end asm

	Loop 

END SUB


#include "inc-copper.bas"

rainbow: 
asm 
	incbin "rainbow.pal" 
	incbin "rainbow.pal" 
end asm      
