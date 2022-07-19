
Sample.bas 			- orchestrator
+- Common.bas 		- this is included in all code 
+- Module1.bas 		- Sub module 1
+- Module2.bas 		- Sub Module 2 
...etc  modules from 0 - 255 can be used 

Modules 

Each module can be up to 32000bytes in size, they will occupy from $6000 - $dd00 MMU3-6 
768 bytes at the end are used for system stack purposes and temporary buffer 

Modules can be called and executed from the orchestrator in this case Sample.bas. This alos has the responsibility to set up the memory space, intialise variable banks, intiate the interrupt routines if used.

To transfer data between banks there is a set varible area set up in banks 24 - this will be paged into slot 2 $4000 - $5fff. The ULA bank is paged out at start up, if you want to draw to ULA you will need to page in bank 10, make your update and page back the variable bank. 

Variables are defined inside the Commmon.bas and begin at $4000. This leaves a huge amount of space for you to assign data. There may be additional drivers that may end up using this second half of this memory but that is tbc....

Inside the Commmon.bas we tell the compiler to start assigning @ $4000

	#define VarAddress $4000
	
Then assign variables like to 

	DIM VarLoadModule AS Ubyte AT VarAddress								' Module to load
	dim VarLoadModuleParameter1 as Ubyte AT VarAddress + 1	' Parameter 1 for the module to load
	DIM VarLoadModuleParameter2 AS Ubyte AT VarAddress + 2	' Parameter 2 for the module to load	

Remember that when we add a variable to in 1 for a byte or 2 for an integer. See Common.bas for more detail.

Also inside Commmon.bas we include routines that we might want to use in all modules. I have attemped to remove the reliance on the ROM as much as possible as this allows us to use the maximum amount of ram. 

Some replacement functions such as print Nstr(byte) is a replacement for STR() that uses the ROM calculator and can causing crashes when we're taking over ram completely.

**EDIT : the above is no longer true as I now patch any ROM calls to ensure banks are in place. STR() VAL() PAUSE SIN COS **

a = GetKey2() will return a key that has been pressed = if a is pressed a will = CODE "a" 

GetKey() will wait for a key press and is a replacement for inkey$ 

PeekString2(address, string$) will assign string$ to a formatted memory location, 2bytes for size then string zero terminated. 

PeekMemLen(address, l, string$) will assign string$ to the memory location starting at address with a length of l 



The Orchestrator - master bank module that lives in MMU7 $E000- $FFFF, this is the first executed part of code and will handle loading in the sub modules as required. The interrupts vector table and service routines are also contained near the end of the memory space. So be aware if you want to temporarily page this out.

Some additional buffers also share this memory address for use with interrupts music & sfx 

Interrupts are intiated in Sample.bas as this allows music and fx to play uninterrupted while swapping modules or drawing the screen. 

$fd00 - $fd60	Reserved for holding control bytes for the AYFX & Music routines. See the nextlib_ints.bas for more info 

$fe00 - $ff01   Reserved for the IM2 interrupt vector table 

The stack is set to $dfff on startup, this should leave ~768 bytes for stack usage! 

nextlib_ints should be include in the master bank and all sub modules that need to interrupt with music. When this library is included in sub modules only small routine are used to set playback bytes while the main interrupts will have been intiated in the master bank. 

CTCs are also available for allowing precise 50Hz timing of PT3 songs and sample play back. When enabled it will patch the vector table

For settings up interrupt music / ayfx you will want to include nextlib_ints.bas into Sample.bas then make a sub routine to initialise everything required. 

; load the song files, play routine, and ayfx bank to required banks: 

LoadSDBank("forest.pt3",0,0,0,56) 				' load music.pt3 into bank 
LoadSDBank("lemotree.pt3",0,0,0,57) 				' load music.pt3 into bank 
LoadSDBank("music.pt3",0,0,0,58) 				' load music.pt3 into bank 
LoadSDBank("vt24000.bin",0,0,0,37) 				' load the music replayer into bank 
LoadSDBank("game.afb",0,0,0,38) 				' load music.pt3 into bank 

InitInterupts(38,37,56)			' set up interrupts sfxbank, playerbank, music bank 


sub InitInterupts(byval sfxbank as ubyte, byval plbank as ubyte, byval musicbank as ubyte)
	 
	InitSFX(sfxbank)						        ' init the SFX engine, sfx are in bank 36
	InitMusic(plbank,musicbank,0000)		        ' init the music engine 33 has the player, 34 the pt3, 0000 the offset in bank 34
	SetUpIM()							            ' init the IM2 code - 
	; or 
	;SetUPCTC()										' if you want to use the ctc sample player 
	 
	PlaySFX(3)                                    	' Plays SFX 
	EnableMusic
	EnableSFX

end sub 

Then from each module you can use 

StopMusic()		- This will also mute the AYs so no hung tones are heard  
PlayMusic() 	- Play / Continue from where stoppe d
NewMusic(bank) 	- start a new tune from bank 

To swap into CTC mode, use:

SetUPCTC()

This will disable the current interrupts then patch the current IM table 

- initmusic in control module {sample.bas}
- this now contains the im code 
- interrupt information 

interrupts are now stored in the orchestrator bank 
