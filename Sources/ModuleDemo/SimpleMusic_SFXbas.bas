'!ORG=32768
'!HEAP=2048

#define IM2
#define NEX
#include <nextlib.bas>
#include <nextlib_ints.bas>
#include <keys.bas>


LoadSDBank("forest.pt3",0,0,0,56) 				' load music.pt3 into bank 
LoadSDBank("vt24000.bin",0,0,0,37) 				' load the music replayer into bank 
LoadSDBank("game.afb",0,0,0,38) 				' load music.pt3 into bank 

InitInterupts(38,37,56)	

do 
    ' forever loop
loop 

sub InitInterupts(byval sfxbank as ubyte, byval plbank as ubyte, byval musicbank as ubyte)
	 
	InitSFX(sfxbank)						        ' init the SFX engine, sfx are in bank 36
	InitMusic(plbank,musicbank,0000)		        ' init the music engine 33 has the player, 34 the pt3, 0000 the offset in bank 34
	SetUpIM()							            ' init the IM2 code 
	 
	PlaySFX(3)                                    	' Plays SFX 
	EnableMusic
	EnableSFX

end sub 