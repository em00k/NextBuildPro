' ------------------------------------------------------------------------------
' Module 2 

' ORG 24576 - $6000
' Usable memory from $6000 to $dd00 minus Heap size 32kB yeah


'; We must specify the master file 
'!master=Sample.NEX				

';if you want to copy the finalised bin
'!copy=h:\Modules\Module1.bin

'; modules always start at $6000 - 24576
'!module 
'!noemu

' MARK: - Init and Main 

Init()
Main()

End 		' Exit module 

#include <nextlib.bas>				' stanbdard nextlib include 
#include "inc-common.bas"			' Common routines used in all modules 

'

dim pcounter    as ubyte 
dim pcounter2   as ubyte 
dim position    as ubyte 
dim sx          as ubyte 
dim sy          as ubyte 
dim dg          as ubyte  = 128
dim dh          as ubyte  = 64
dim delay       as ubyte 
dim dhdelay     as ubyte  = 16
dim a           as ubyte 

' This is the intialisation of the module 

Sub Init()
	asm 
		nextreg SPRITE_CONTROL_NR_15,%00000011			; ensure sprites are on 
	end asm 
end sub 

Sub Main()
	
	' Main module routine 
    CLS256(0)
	InitSprites2(63,0,26)								' init sprites in bank 26 for mouse 
	L2Text(0,0,"This is Module 2",28,0)					' show some infos 
    L2Text(0,1,"Press any key to exit module",28,0)					' show some infos 
    L2Text(0,4,"Try keys 1 & 2",28,0)					' show some infos 
	Do 

		WaitRetrace(1)									' wait vblank
        draw_sprites()

        a = GetKey2

        if a = code "1"
            dg = dg + 1
            L2Text(0,2,str(dg),28,255)	

        elseif a = code "2"
            dh = dh + 1
            L2Text(0,3,str(dh),28,255)	

        elseif a = code " "
            exit do 
        endif 

        while GetKey2()
        wend

        ' if dhdelay = 0
        '     dh = dh + 1 
        '     dhdelay = 2
        ' else 
        '     dhdelay = dhdelay - 1
        ' endif 
	Loop 



    VarLoadModule=ModuleSample1

end sub 

sub draw_sprites()

    dim x       as ubyte 
    dim dx      as ubyte 
    dim dy      as ubyte 
    dim max     as ubyte 

    pcounter    = 0 
    pcounter2   = 0 
    max         = 64

    for x = 0 to max-1

        sx=peek(@sintable+((position + pcounter) ))                               ' adds rotation around middle base 
        sy=peek(@sintable+((position + 64 + pcounter) ))

        dx=peek(@sintable2+((x +  pcounter2) ))   >>2                            ' adds rotation around middle base 
        dy=peek(@sintable2+((x + 64 + pcounter2) )) >>2

        pcounter = pcounter + dg ' + x/16
        pcounter2 = dh + pcounter2 + 3 ' + x/16

        if delay = 0 
            
            position = (position + 1) 
            delay = 64
        else 
            delay = delay -1 
        endif 

        UpdateSprite(cast(uinteger,128+sx-dx),96+sy-dy,x,0,0,0 )

    next 

end sub 

sintable:
asm 
    db 64,62,60,59,57,56,54,53,51,49,48,46,45,43,42,40
    db 39,37,36,35,33,32,30,29,28,27,25,24,23,22,20,19
    db 18,17,16,15,14,13,12,11,10,9,8,8,7,6,6,5
    db 4,4,3,3,2,2,1,1,1,0,0,0,0,0,0,0
    db 0,0,0,0,0,0,0,1,1,1,2,2,2,3,3,4
    db 5,5,6,7,7,8,9,10,11,11,12,13,14,15,16,18
    db 19,20,21,22,23,25,26,27,28,30,31,33,34,35,37,38
    db 40,41,43,44,46,47,49,50,52,53,55,56,58,60,61,63
    db 64,66,67,69,71,72,74,75,77,78,80,81,83,84,86,87
    db 89,90,92,93,94,96,97,99,100,101,102,104,105,106,107,108
    db 109,111,112,113,114,115,116,116,117,118,119,120,120,121,122,122
    db 123,124,124,125,125,125,126,126,126,127,127,127,127,127,127,127
    db 127,127,127,127,127,127,127,126,126,126,125,125,124,124,123,123
    db 122,121,121,120,119,119,118,117,116,115,114,113,112,111,110,109
    db 108,107,105,104,103,102,100,99,98,97,95,94,92,91,90,88
    db 87,85,84,82,81,79,78,76,74,73,71,70,68,67,65,64
    db 64,62,60,59,57,56,54,53,51,49,48,46,45,43,42,40
    db 39,37,36,35,33,32,30,29,28,27,25,24,23,22,20,19
    db 18,17,16,15,14,13,12,11,10,9,8,8,7,6,6,5
    db 4,4,3,3,2,2,1,1,1,0,0,0,0,0,0,0
    db 0,0,0,0,0,0,0,1,1,1,2,2,2,3,3,4
    db 5,5,6,7,7,8,9,10,11,11,12,13,14,15,16,18
    db 19,20,21,22,23,25,26,27,28,30,31,33,34,35,37,38
    db 40,41,43,44,46,47,49,50,52,53,55,56,58,60,61,63
    db 64,66,67,69,71,72,74,75,77,78,80,81,83,84,86,87
    db 89,90,92,93,94,96,97,99,100,101,102,104,105,106,107,108
    db 109,111,112,113,114,115,116,116,117,118,119,120,120,121,122,122
    db 123,124,124,125,125,125,126,126,126,127,127,127,127,127,127,127
    db 127,127,127,127,127,127,127,126,126,126,125,125,124,124,123,123
    db 122,121,121,120,119,119,118,117,116,115,114,113,112,111,110,109
    db 108,107,105,104,103,102,100,99,98,97,95,94,92,91,90,88
    db 87,85,84,82,81,79,78,76,74,73,71,70,68,67,65,64

    db 0,-1,-3,-4,-6,-7,-9,-10,-11,-12,-13,-14,-14,-15,-15,-15
    db -15,-15,-15,-15,-14,-13,-12,-11,-10,-9,-8,-6,-5,-3,-2,0
    db 0,2,3,5,6,8,9,10,11,12,13,14,15,15,15,15
    db 15,15,15,14,14,13,12,11,10,9,7,6,4,3,1,0
    db 0,-1,-3,-4,-6,-7,-9,-10,-11,-12,-13,-14,-14,-15,-15,-15
    db -15,-15,-15,-15,-14,-13,-12,-11,-10,-9,-8,-6,-5,-3,-2,0
    db 0,2,3,5,6,8,9,10,11,12,13,14,15,15,15,15
    db 15,15,15,14,14,13,12,11,10,9,7,6,4,3,1,0
end asm 

sintable2:
asm 
    db 127,118,108,99,90,81,72,64,56,48,41,34,28,22,17,13
    db 9,6,3,1,0,0,0,1,2,4,7,11,15,20,25,31
    db 38,45,52,60,68,77,85,94,104,113,122,132,141,150,160,169
    db 177,186,194,202,209,216,223,229,234,239,243,247,250,252,253,254
    db 254,254,253,251,248,245,241,237,232,226,220,213,206,198,190,182
    db 173,164,155,146,136,127,118,108,99,90,81,72,64,56,48,41
    db 34,28,22,17,13,9,6,3,1,0,0,0,1,2,4,7
    db 11,15,20,25,31,38,45,52,60,68,77,85,94,104,113,122
    db 132,141,150,160,169,177,186,194,202,209,216,223,229,234,239,243
    db 247,250,252,253,254,254,254,253,251,248,245,241,237,232,226,220
    db 213,206,198,190,182,173,164,155,146,136,127,118,108,99,90,81
    db 72,64,56,48,41,34,28,22,17,13,9,6,3,1,0,0
    db 0,1,2,4,7,11,15,20,25,31,38,45,52,60,68,77
    db 85,94,104,113,122,132,141,150,160,169,177,186,194,202,209,216
    db 223,229,234,239,243,247,250,252,253,254,254,254,253,251,248,245
    db 241,237,232,226,220,213,206,198,190,182,173,164,155,146,136,127
end asm 