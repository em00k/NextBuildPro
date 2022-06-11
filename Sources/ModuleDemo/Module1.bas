' ------------------------------------------------------------------------------
' - BankManager Sample v.2.0 ---------------------------------------------------
' ------------------------------------------------------------------------------
' - Sample module 1 ------------------------------------------------------------
' ------------------------------------------------------------------------------

' ORG 24576 - $6000
' Fixed bank located at $6000 to $7fff
' Usable memory from $6000 to $dd00 minus Heap size 32kB yeah
'!master=Sample.NEX
'!copy=h:\Modules\Module1.bin
'!org=24576
'#!heap=768
'!module 


'local vars 
dim	oldmox,mbutt 			as ubyte 
dim mox, moy, oldmoy, spry 	as ubyte 
dim r,g,b,index				as ubyte 
dim sprx,c,rgb9				as uinteger
dim button_pressed 			as ubyte 

const font 	as ubyte =	28 
dim LUT2BITTO8BIT(3) as ubyte => {0,$55,$AA,$FF}
dim LUT3BITTO8BIT(7) as ubyte => {0,$24,$49,$6D,$92,$B6,$DB,$FF}
 

' PAPER 0 : INK 7 : CLS 

Init()
Main()

End

#define IM2
#define NOSP 
#include <nextlib.bas>
#include <nextlib_ints_ctc2.bas>
#include "inc-Common.bas"
#include "inc-mouse.bas"

function rgb92rgb24(rgb9 as uinteger) as uinteger 

	r = LUT3BITTO8BIT(cast(Ubyte,rgb9 >> 6 Band 7))
	g = LUT3BITTO8BIT(cast(Ubyte,rgb9 >> 3 Band 7))
	b = LUT3BITTO8BIT(cast(Ubyte,rgb9 Band 7))
 
end function

function rgb82rgb24(rgb8 as ubyte) as uinteger 

	'r = PeekA(?LUT3BITTO8BIT+(rgb8 >> 5))
	'g = PeekA(?LUT3BITTO8BIT+(rgb8 >> 2) & 7)
	'b = PeekA(?LUT2BITTO8BIT+(rgb8 & 3))

	r = LUT3BITTO8BIT(cast(Ubyte,rgb8 >> 5))
	g = LUT3BITTO8BIT(cast(Ubyte,rgb8 >> 2) band 7)
	b = LUT2BITTO8BIT(cast(Ubyte,rgb8 band 3))
 
end function

Sub Init()
	'BBREAK
	asm 
		nextreg SPRITE_CONTROL_NR_15,%00000001
		ei 
	end asm 	
	PlayMusic()
	ClipLayer2(0,255,0,255)
	copper_stop()
	reset_palette()
	' SetCTCSampleTable(@ctc_sample_table)
end sub 



Sub Main()

	dim key as ubyte 

	CLS256(0)  

	DisplayPalette()

	L2Text(0,0,"NEXT PALLET EDITOR",font,0)
	L2Text(20,3,"- R +",font,0)
	L2Text(20,5,"- G +",font,0)
	L2Text(20,7,"- B +",font,0)

	InitSprites2(16,0,26)		' init sprites in bank 26

	
	Do 
	

		asm 
			nextreg TRANSPARENCY_FALLBACK_COL_NR_4A,68
		end asm 

		ProcessMouse()
		UpdatePointer()
		UpdateText(0,20)

		asm 
			nextreg TRANSPARENCY_FALLBACK_COL_NR_4A,0
		end asm 

		if mouse_mbutt band %11 = 1 and key = 0 

			click()
			'BBREAK
			PlaySFX(index)
			key = 1 
		elseif mouse_mbutt band %11 = 3

			L2Text(0,22,"no click",font,255)
			' L2Text(20,20,"zone",font,255)
			button_pressed = 0 
			
			key = 1 
		else 
			key = 0 
		end if 

        if mouse_mbutt band 3 =2 
            VarLoadModule=ModuleSample2
            exit do 
        endif 

		WaitRetrace(1)
		
	Loop 

end sub 


sub GetRGB(index as ubyte)

	dim a,b 	as ubyte 
	dim c 		as uinteger

	NextReg(PALETTE_CONTROL_NR_43,%00010000)  	' l2 pal 1
	NextRegA($40,index) ' reset pal index
	a=GetReg($41)			' read first pal byte
	b=GetReg($44)		

	c=b bor a<<1

	rgb92rgb24(c)
	'rgb82rgb24(c)

	L2Text(27,3,NStr(r),font,1)
	L2Text(27,5,NStr(g),font,1)
	L2Text(27,7,NStr(b),font,1)

end sub 

sub UpdateText(x as ubyte,y as ubyte)

	L2Text(x,y,NStr(mox>>3)+NStr(moy>>3),font,1)
	L2Text(x,y+1,NStr(mbutt band 3),font,1)

end sub 

sub click()
	
	dim tx,ty as ubyte 

	if mouse_mbutt band 3 =1  				' left mouse 
		
		L2Text(0,22,"CLICKED",font,0)
		button_pressed = 1 			   	' mouse button preessed 

		tx = (mouse_mox>>3)-2
		ty = (mouse_moy>>3)-2

		if tx >= 0 and tx <= 15 
			if ty >= 0 and ty <= 15
				index = tx + ( ty * 16)
				L2Text(26,20,"xxxxxx",font,255)
				L2Text(20,20,"INDEX "+NStr(index),font,0)
				GetRGB(index)
			endif 
		endif 
		
	endif 
	' PlaySample(2)
end sub 


sub DisplayPalette()
	dim x, xx, y, yy, p as ubyte 
	const offset as ubyte 	= 2*8 
	p = 0 
	for y = 0 to 15 
		for x = 0 to 15 
			for yy=0 to 7 
				for xx=0 to 7 	
					PlotL2(offset+(x<<3)+xx,offset+(y<<3)+yy,p)
				next xx 
			next yy 
			p = p + 1 
		next x
	next y 
end sub 
#include "inc-copper.bas"


