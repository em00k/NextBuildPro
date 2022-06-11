..\snasm -map timer.asm timer.snx
if ERRORLEVEL 1 goto doexit

rem simple 48k model
..\CSpect.exe -tv -map=timer.sna.map -zxnext -mmc=.\ timer.snx

:doexit
