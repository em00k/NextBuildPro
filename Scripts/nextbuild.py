#!/usr/bin/env python3
# v7.9 NextBuild / NextLib by David Saphier (c) 2021 / em00k 15-Feb-2022
# ZX Basic Compiler by (c) Jose Rodriguez
# Thanks to Jari Komppa for help with the cfg parser 
# Extra thanks to Jose for help integrating into the zxb python modules and nextcreator.py 
# Big thanks to D Rimron Soutter as always 
# Thanks to Deufectu for the original module concept
# This file takes a zx basic source file and compiles then generates a NEX file. 
#
import sys
import subprocess, os, platform

# add a bunch or dirs to the path 
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
SCRIPTS_DIR = os.path.abspath(os.path.join(BASE_DIR, 'Scripts'))  # ZX BASIC root path
EMU_DIR = os.path.abspath(os.path.join(BASE_DIR, 'Emu/CSpect'))  # ZX BASIC root path
ZXBASIC_DIR = os.path.abspath(os.path.join(BASE_DIR, 'zxbasic'))  # ZX BASIC root path
LIB_DIR = os.path.join(ZXBASIC_DIR, 'src/arch/zxnext/library')
SRC_DIR = os.path.join(ZXBASIC_DIR, 'src')
TOOLS_DIR = os.path.join(ZXBASIC_DIR, 'tools')


sys.path.append(SRC_DIR)  # append it to the list of imports folders
sys.path.append(SCRIPTS_DIR)  # append it to the list of imports folders
sys.path.append(LIB_DIR)  # append it to the list of imports folders
sys.path.append(ZXBASIC_DIR)  # append it to the list of imports folders
sys.path.append(TOOLS_DIR)  # append it to the list of imports folders

##from shutil import copyfile
from src.zxbc import zxbc
from src.zxbc import version
from tools import nextcreator
from datetime import datetime
import txt2nextbasic
import time
import glob
import shutil 
import argparse

global heap, orgfound, destinationfile, createasm, headerless, optimize, bmpfile, noemu, org, head_file, inputfile ,autostart, nextzxos
global filename_path,filename_extension,filename_noextension,copy,gentape,makebin,binfile,pcadd,sysvars, arch, no_nex 
global module, master, runmaster

start=datetime.now()


# parse command line arguments 
# 
parser = argparse.ArgumentParser(description='NextBuild.py Pre Processor')
parser.add_argument('-b', dest='file', type=ascii, required = True, help='.bas file to process - required')
parser.add_argument('-q' ,dest='quiet', action='store_true', help='Dont show splash')
parser.add_argument('-m', dest='modules', action='store_true' , help='Compile & Build module files')
parser.add_argument('-t', dest='tape', action='store_true' , help='Build a TAP file')
parser.add_argument('-l', dest='runmaster', action='store_true' , help='Build a TAP file')
parser.add_argument('-s', dest='singlefile', action='store_true' , help='Build a TAP file')

args = parser.parse_args()

inputfile = args.file.strip('\'')   

# show info 
if args.quiet == 0: 
    print("===============================================================================================")
    print("NextBuild v8.0    : David Saphier / em00k - 15-May-2022     https://github.com/em00k/NextBuild")
    print("ZX Basic Compiler : Jose Rodriguez aka Boriel               https://zxbasic.readthedocs.io/")
    print("Cspect Emulator   : Mike Dailly                             https://cspect.org")
    print("===============================================================================================")

    print("Input File : " + inputfile)
    print("")


head_tail = os.path.split(inputfile)            # get the path of the file 
sys.path.append(head_tail[0])                   # add to paths 
os.chdir(head_tail[0])                          # make sure we're in the working source folder 
copy = 0                                        # for setting up copying to another location 
heap = "2048"                                   # default heap 
orgfound = 0
destinationfile = "" 
createasm=0
headerless = 0 
optimize = '4'
bmpfile = None
noemu = 0
nextzxos = 0 
makebin = 0 
no_nex = 0 
module = args.modules
gentape = args.tape
autostart = 0 
filename_path = ""
master = "" 
filename_extension = ""
filename_noextension = ""
pcadd = "57344"                     # default for nextbuild 8 modules 
org = "0"
arch = "--arch=zxnext"
sysvars = 0 

# need to get the fname and splice off extension 
filenamenoext = head_tail[1].split('.')[1-1]
filename_extension = head_tail[1]
filename_path = head_tail[0]

# procs 

def CheckForBasic():
    # was ther file a .bas?
    testfname = head_tail[1].split('.')[1-2]
    if testfname == 'bas':
        print("basic file")
    else:
        print('Not a basic file')
        sys.exit(1)    

def GenerateLoader():

        #filename =  os.path.split(inputfile) 
        # get path and filename
        #dest = inputfile.split(':')[1-2] 

        if makebin == 1: 
            # we are making a bin not nex 
            print('Making a bin')
            ext = '.bin'
            txt2nextbasic.b_makebin = 1 
            outfile = os.path.split(binfile)
            outfilenoext = outfile[1].split('.')[1-1]
            print(outfilenoext)

        else:
            if no_nex == 1:
                print("Do not create NEX")
                ##copy(head_tail[0]+'/module.*', head_tail[0]+'/data/')

                return
            else: 
                ext = '.nex'
                txt2nextbasic.b_makebin = 0
                outfilenoext = filenamenoext
                ParseNEXCfg()
                CreateNEXFile()

        txt2nextbasic.b_name = outfilenoext+ext              # filename of basic file 
        txt2nextbasic.b_start = int(org)

        if autostart == 1: 
            txt2nextbasic.b_auto = 1                 # filename of basic file 
            txt2nextbasic.b_loadername = 'autoexec.bas'              # filename of basic file 
            txt2nextbasic.main()
            # copies the autoexec.bas 
            if nextzxos == 1: 
                subprocess.run([EMU_DIR+'/hdfmonkey.exe','put','/CSpect/cspect-next-2gb.img','autoexec.bas','/nextzxos/autoexec.bas'])
        else:
            txt2nextbasic.b_auto = 0 

        print("BAS created OK! All done.")

        if makebin == 1: 
            loaderfile = filenamenoext+'loader.bas'

            txt2nextbasic.b_loadername = loaderfile              # filename of basic file 
            txt2nextbasic.b_auto = 0 
            txt2nextbasic.main()

            subprocess.run([EMU_DIR+'/hdfmonkey.exe','put','/CSpect/cspect-next-2gb.img',loaderfile,'/'+loaderfile])
        
        subprocess.run([EMU_DIR+'/hdfmonkey.exe','put','/CSpect/cspect-next-2gb.img',filenamenoext+ext,'/'+outfilenoext+ext])
        #subprocess.run([EMU_DIR+'\launchnextzxos.bat',head_tail[0]+'/Memory.txt',EMU_DIR])
        if noemu == 0:
            subprocess.Popen([EMU_DIR+'/launchnextzxos.bat',head_tail[0]+'/Memory.txt',EMU_DIR])


def CreateNEXFile():
    
    tmp_ath = "" 

    if no_nex == 1:
            #print("Do not create NEX, will copy modules to data")
            file_size = os.path.getsize(filenamenoext+'.bin')
            percent=(file_size*100)/32000
            print("BIN filesize :  "+str(file_size)+"b - "+str(percent)[:4]+"% of 32000b available")
            return

            #if copy == 1: 
            #    shutil.copy(head_tail[0]+'bin', head_tail[0]+'/data/')

    else: 
        try:        
            # now use nexcreator.py to creat a NEX using the config file 
            print("====================================================")
            print("Generating NEX : "+head_tail[0]+'/'+filenamenoext+'.nex')
            print("")
            nextcreator.parse_file(head_tail[0]+'/'+filenamenoext+'.cfg')
            nextcreator.generate_file(filenamenoext+'.nex')            
            print("")
            print("Compile Log  :  "+head_tail[0]+"/Compile.txt")
            print("Memory Log   :  "+head_tail[0]+"/Memory.txt")
            print("")
            file_size = os.path.getsize(filenamenoext+'.nex')
            print("NEX filesize : "+str(file_size))
            print("NEX created OK! All done.")
        except:
            print("ERROR creating NEX file!")
            raise 
            sys.exit(1) 

def ParseNEXCfg():
        global sysvars

        if module == 1:
            print("Copy to ../release/")
            try:
                shutil.copy(head_tail[0]+'/'+filenamenoext+".bin", head_tail[0]+'/release/')
            except:
                print("Failed to copy to release folder!")

            print("Copy to ../data/")
            try:
                shutil.copy(head_tail[0]+'/'+filenamenoext+".bin", head_tail[0]+'/data/')
            except:
                print("Failed to copy data!")
            return
        CRLF = "\r\n"
        print("====================================================")
        print("Generating Nexcreator Config ...")
        print("")

        # default top lines 
        outstring = "; Minimum core version" + CRLF
        outstring += "!COR3,0,0" + CRLF
        # we include sysvars 
        if sysvars == 0: 
            outstring += "!MMU../../Tools/sysvars.bin,10,$1C00" + CRLF

        defaultpc = int(org)

        # now read through full source for MAIN_ADDRESS 
        # this is for headerless but seems broken
        # try:
            # print("Looking for .__MAIN_PROGRAM__...")
            # with open(head_tail[0]+"/Memory.txt" ,'rt') as f:
                # lines = f.read().splitlines()
                # curline = 0
                # for x in lines:
                    # xl = x.lower()
                    # main_pos = xl.find(".__main_program__")         # we fonud '!ORG= so now set var org 
                    # if main_pos != -1:
                        # pc = x.split(":")[1-1]
                        # defaultpc = int(pc,16)             
                        # print("Found main_pos    :  "+str(defaultpc))  
                    # # orgfound = 1
                
                    # curline += 1
                    # # if the line > 64 then quit 
                    # if curline == 64:
                        # break
        # except:
            # print("Uknown error opening source file")
            # raise 
        if bmpfile != None:
                
            outstring += '!BMP8'+bmpfile+',0,0,0,0,255' + CRLF
            
        try:
            with open(inputfile, 'rt') as f:
                lines = f.read().splitlines()
                curline = 0 
                trimmed = 0 
                outstringa =""
                for x in lines:
                    # replace any brackets with commas so we can do string split 
                    x = x.replace(")", ",")
                    x = x.replace("(", ",")
                    # convert to lower case so xl.find() will be case insensitive
                    xl = x.lower().strip()
                    curline += 1
                    # look for SD command 
                    ldsd_pos = xl.find("loadsdbank,")   
                    if ldsd_pos != -1:
                        # if it isnt the main SUB or a commented out line
                         if xl.find("sub") == -1 and xl[0] != "'":
                            # get the filename + add the data path 
                            partname = x.split('"')[2-1]
                            filename = "./data/" + partname

                            try:
                                f = open(filename)
                                f.close()
                                # and load address in bank 
                                offset = x.split(',')[3-1]
                                offset = offset.replace("$", "0x")
                                offval = int(offset,16) & 0x1fff
                                if offset.find("0x") == -1: 
                                    offval = int(offset,10) & 0x1fff

                                #offset from start of file 
                                fileoffset = x.split(',')[5-1]
                                #creates a trimmed copy of the bank
                                if int(fileoffset) > 0:
                                    floffset = int(fileoffset)
                                    print("File "+partname+" has an offset of : "+str(floffset))
                                    orig_file_content = open(filename, 'rb').read()
                                    new_file_content = orig_file_content[floffset:]
                                    with open('./data/tr_'+partname[:-4]+str(trimmed)+'.bnk', 'wb') as f:
                                        f.write(new_file_content)                          
                                        filename = './data/tr_'+partname[:-4]+str(trimmed)+'.bnk'
                                        print("Trimmed as :"+filename)
                                        trimmed+1
                                
                                # get the bank 
                                bank = x.split(',')[6-1]   

                                # add to our outstring 
                                outstring += "; " + x + CRLF
                                outstring += "!MMU" + filename + "," + bank + ",$"+("000" + hex(offval)[2:])[-4:] + CRLF

                            except IOError:
                                print("##ERROR - Failed to find file :"+filename)
                                print("Please make sure this file exist!")
                                print("")
                                sys.exit(1) 

            # generate PC and SP for cfg 



            sp = int(org) -2

            # if PC = 0 then its a non autostarting NEX file.
            #print(pcadd)
            if int(pcadd) == 0:   
                defaultpc = pcadd
                sp = int(pcadd)
                                
            pc = int(defaultpc)

            outstring += "!PCSP$" + ("000" + hex(pc)[2:])[-4:] + ",$" + ("000"+hex(sp)[2:])[-4:] + CRLF

            # outstring += "!BANK15" + CRLF

            # this works out which rambank we need to put our code in depending on the ORG 
            
            if int(org)>=0x4000 and int(org)<=0x7fff:
                rambank="5"
            elif int(org)>=0x8000 and int(org)<=0xbfff:
                rambank="2" 
            elif int(org)>=0xc000 and int(org)<=0xffff:
                rambank="0"   
            elif int(org)>=0x0000 and int(org)<=0x3fff:
                rambank="7"   
            codestart = int(org) % 0x4000
            
            outstring += filenamenoext+".bin,"+rambank+",$"+("000" + hex(codestart)[2:])[-4:] + CRLF

            # save config 

            with open(filenamenoext+".cfg", 'wt') as f:
                f.write(outstring)
            print("Saved config file : "+filenamenoext+".cfg")
        except:
            raise
            print("ERROR "+xl)
            sys.exit(0) 

def ParseDirectives():
    global heap, orgfound, destinationfile, createasm, headerless, optimize, bmpfile, noemu, org, head_file, inputfile ,autostart, nextzxos
    global filename_path,filename_extension,filename_noextension,copy,gentape,makebin,binfile,pcadd,sysvars,origin_pos, arch
    global no_nex, module, master 

    try:
        print("Procesing .bas header")
        print("")
        
        org="32768"

        with open(inputfile ,'rt') as f:
            lines = f.read().splitlines()
            curline = 0
            for x in lines:
                xl = x.lower().strip().split(" ")[0]   # strips off comments
               # print(xa)
               # xl = xa.split()
               # print(xl)
                org_pos = xl.find("'!org=")         # we fonud '!ORG= so now set var org 
                if org_pos != -1:
                    # x = x.split()
                    org = x.split("=")[2-1]
                    print("Found ORG    :  "+org)  
                    orgfound = 1
                hea_pos = xl.find("'!heap=")        # same for heap 
                if hea_pos != -1:
                    heap = x.split("=")[2-1]
                    print("Found HEAP   :  "+heap)          
                optimize_pos = xl.find("'!opt=")        # same optimisations 
                if optimize_pos != -1:
                    optimize = x.split("=")[2-1]
                    print("Found OPT    :  "+optimize)       
                module_pos = xl.find("'!module")        # configures a module 
                if module_pos != -1:
                    noemu = 1 
                    no_nex = 1 
                    no_sysvars = 1 
                    module = 1 
                    pcadd = "24576"                       # modules always start at 24576 / $6000
                    org = "24576"

                    # headerless = 1 
                    print("Is a module? :  True")       

                noemeu_pos = xl.find("'!noemu")        # same optimisations 
                if noemeu_pos != -1:
                    noemu = 1 
                    # print("Do Not Run Emu ")
                copy_pos = xl.find("'!copy=")        # and copy         
                if copy_pos != -1:
                    copy = 1
                    destinationfile = x.split("=")[2-1]
                    print("Found copy   :  "+destinationfile)
                asm_pos = xl.find("'!asm")        # and asm
                if asm_pos != -1:
                    noemu = 1
                    createasm=1
                    print("Found ASM   :   Will generate ASM file")
                head_pos = xl.find("'!headerless")        # and headerless mode 
                if head_pos != -1:
                    headerless = 1
                    print("Headerless  :   Will generate headerless binary")
                bmp_pos = xl.find("'!bmp=")                 # adds loading screen
                if bmp_pos != -1:
                    bmpfile = './data/'+x.split("=")[2-1]
                    print("Loading BMP :   "+bmpfile)
                nextzxos_pos = xl.find("'!nextzxos")        # launches in nextzxos
                if nextzxos_pos != -1:
                    nextzxos = 1 
                    noemu == 1

                auto_pos = xl.find("'!autostart")        # creates auto start for nextzxos
                if auto_pos != -1:
                    autostart = 1 
                    print("Found autostart")
                    noemu == 1

                make_bin = xl.find("'!bin")        # for saving a bin 
                if make_bin != -1:
                    makebin = 1 
                    binfile = x.split("=")[2-1]
                    print("Found bin    :  "+binfile)
                    noemu == 1

                pc_add = xl.find("'!pc")        # allows different pc than org 
                if pc_add != -1:
                    address = x.split("=")[2-1]
                    pcadd = address
                    print("PC Value     :  "+pcadd)

                no_sysvars = xl.find("'!nosys")        # exclude sysvars 
                if no_sysvars != -1:
                    sysvars = 1 
                    print("No Sys Vars")

                no_sysvars = xl.find("'!master=")        # exclude sysvars 
                if no_sysvars != -1:
                    master = x.split("=")[2-1]
                    print("Found master :  "+master)

                check_arch = xl.find("'!zx")        # use 48k arch 
                if check_arch != -1:
                    arch = "--arch=zx48k"
                    print("arch=zx48k")

                check_nex = xl.find("'!nonex")        # dont create a nex file 
                if check_nex != -1:
                    print("Do not create nex")
                    no_nex = 1

                origin_pos = xl.find("'!origin=")        # and origin of compile, redirect our input to this. mode 
                if origin_pos != -1:
                    print("FOUND ORIGIN")
                    f.close()
                    print("OLD: "+inputfile)
                    inputfile = os.path.join(head_tail[0],x.split("=")[2-1])
                    
                    print("NEW: "+inputfile)
                    print("SWITCHING COMPILE ORIGIN:   "+inputfile)
                    ParseDirectives()

                    return
                curline += 1
                # if the line > 64 then quit 
                if curline == 64:
                    break


    except:
        print("Uknown error opening source file")
        raise 
    if args.singlefile == 1:         # true 
        module = 0 
        master = filenamenoext+'.NEX'

    if makebin == 1: 
        if nextzxos == 0:
            print('Can only use !bin with !nextzxos')
            makebin = 0 
        copy = 0 

    if nextzxos == 1: 
        print("Will launch from NextZXOS.")   

    if orgfound == 0: 
        print("Never found ORG")             # if no org found, we had set it 32768
        print("Default ORG  :  "+org)

def ZXBCompile():

    if args.quiet == 0: 
        print("Working Dir  : ",head_tail[0])
    #print("Source       :  "+inputfile)
    #print("Filename     :  "+filenamenoext)

    # this is the full call to zxb 

    #print("====================================================")
        print("Compiling    :  "+inputfile)
        print("ZXbasic ver  :  "+version.VERSION)
        print("Architechure :  "+arch)
        print("")

    if args.quiet == 1:
        print("Compiling    :  "+inputfile)

    if createasm == 0:
        # disable warnings for fastcall with param
        # disable warnings for unused function 
        # disable warnings for functions never called 
        if headerless == 1: 
            #test=zxbc.main([inputfile,'--headerless','-W','160','-W','140','-W','150','-W','170','-S', org,'-O',optimize,'-H',#heap,'-M',inputfile+'.map','-e','Compile.txt','-o',head_tail[0]+'/'+filenamenoext+'.bin','-I', LIB_DIR,'-I', #SCRIPTS_DIR])

            test=zxbc.main([inputfile,arch,'--headerless','-W','160','-W','140','-W','150','-W','170','-W','190','-S', org,'-O',optimize,'-H',heap,'-M',inputfile+'.map','-o',head_tail[0]+'/'+filenamenoext+'.bin','-I', LIB_DIR,'-I', SCRIPTS_DIR])


        else: 
            # '-e','Compile.txt'
            if gentape  == 1: 
                test=zxbc.main([inputfile,'-W','160','-W','140','-W','150','-W','170','-W','190','-S', org,'-O',optimize,'-H',heap,'-M',inputfile+'.map','-t','-B','-a','-o',head_tail[0]+'/'+filenamenoext+'.tap','-I', LIB_DIR,'-I', SCRIPTS_DIR])
            else: 
                test=zxbc.main([inputfile,arch,'-W','160','-W','140','-W','150','-W','170','-W','190','-S', org,'-O',optimize,'-H',heap,'-M',inputfile+'.map','-o',head_tail[0]+'/'+filenamenoext+'.bin','-I', LIB_DIR,'-I', SCRIPTS_DIR])

    else:
        test=zxbc.main([inputfile,'-S', org,'-O',optimize,'-H',heap,'-e','Compile.txt','-A','-o',head_tail[0]+'/'+filenamenoext+'.asm','-I', LIB_DIR,'-I', SCRIPTS_DIR])
        noemu = 1 
        copy = 0   
    if test == 0:
        if args.quiet == 0:
            print("YAY! Compiled OK! ")

        if gentape  == 1: 
            print("")
            print("Compile Log  :  "+head_tail[0]+"/Compile.txt")
            print("Memory Log   :  "+head_tail[0]+"/Memory.txt")
            print("")
            print("TAP created OK! All done.")
            timetaken = str(datetime.now()-start)
            print('Overall build time : '+timetaken[:-5]+'s')
            sys.exit(0)
        if nextzxos == 1: 
            print("Generating NextZXOS loader.bas")

            GenerateLoader()

            timetaken = str(datetime.now()-start)
            print('Overall build time : '+timetaken[:-5]+'s')    
            sys.exit(1)   
    else:
    # # # if compilation fails open the compile output as a system textfile
    # #     print("Compile FAILED :( "+str(test))
    # #     #os.system('start notepad compile.txt')
    # #     if platform.system() == 'Darwin':       # macOS
    # #         subprocess.call(('open', 'compile.txt'))
    # #     elif platform.system() == 'Windows':    # Windows
    # #         os.startfile('compile.txt')
    # #     else:                                   # linux variants
    # #         subprocess.call(('xdg-open', 'compile.txt'))
    # #     print("Compile Log  :  "+head_tail[0]+"/Compile.txt")
        sys.exit(-1)

    if createasm == 1:
        # display this massive message so you dont get confused when code isn't changing in your nex..... ;)
        print(" █████╗ ███████╗███╗   ███╗")
        print("██╔══██╗██╔════╝████╗ ████║")
        print("███████║███████╗██╔████╔██║")
        print("██╔══██║╚════██║██║╚██╔╝██║")
        print("██║  ██║███████║██║ ╚═╝ ██║")
        print("╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝")
        print("Generated    : "+head_tail[0]+'/'+filenamenoext+'.asm')
        print("Compile Log  :  "+head_tail[0]+"/Compile.txt")
        print("Exiting.")
        sys.exit(1) 

def CopyToDestination():
    
    if copy == 1:
        filename_path = os.path.split(destinationfile) 
        filename_extension = filename_path[1].split('.')[1-2]
        filename_noextension = filename_path[1].split('.')[1-1]

        print("Sleep 1 secs")

        time.sleep(1.0)

        if no_nex == 1: 
            filename_extension = '.bin'
        else:
            filename_extension = '.nex'


        print("Copy "+filenamenoext+filename_extension+" to : "+destinationfile)


        if no_nex == 1:
            src = head_tail[0]+'/'+filenamenoext+filename_extension 
            dst = filename_path[0]
            # print(src)
            # print(dst)
            try:
                shutil.copy(head_tail[0]+'/'+filenamenoext+filename_extension, filename_path[0])
            except:
                print("Failed to copy to destination "+dst)
            return 

        try:

            if no_nex == 0: 
                filename_path = os.path.split(destinationfile) 
                filename_extension = filename_path[1].split('.')[1-2]
                filename_noextension = filename_path[1].split('.')[1-1]

                txt2nextbasic.b_makebin = 1 
                txt2nextbasic.b_name = filename_path[1]              # filename of basic file 
                txt2nextbasic.b_start = int(org)

                txt2nextbasic.b_auto = 0                                # filename of basic file 
                txt2nextbasic.b_loadername = 'loader.bas'              # filename of basic file 
                txt2nextbasic.main()

            if filename_extension=='bin' and no_nex == 0:
                print('its a bin ')
                try:
                    # copyfile(head_tail[0]+'/loader.bas', filename_path[0]+filename_noextension+'loader.bas')
                    #copyfile(head_tail[0]+'/'+filenamenoext+'.'+filename_extension, filename_path[0]+'/'+filename_noextension+'.'+filename_extension)


                    shutil.copy(head_tail[0]+'/'+filenamenoext+filename_extension, filename_path[0])

                    #print('Copied '+filename_path[0]+filename_noextension+'loader.bas')
                    print('Copied '+filename_path[0]+'/'+filename_noextension+'.'+filename_extension)
                except:
                    print('failed to copy'+head_tail[0]+'/loader.bas to '+filename_path+filenamenoext+'loader.bas')
            else:
                try: 
                    # Copy to destination 
                  #  shutil.copy(head_tail[0]+'/'+filenamenoext+filename_extension, filename_path[0])
                    shutil.copy(head_tail[0]+'/'+filenamenoext+"."+filename_extension, destinationfile)
                    
                except:
                    print('Failed to copy '+destinationfile)
                    
            if autostart == 1 : 
                    copyfile(head_tail[0]+'/loader.bas', filename_path[0]+'nextzxos/autoexec.bas')
                    print('Copied '+filename_path[0]+'nextzxos/autoexec.bas')    

                    print("Copy SUCCESS!")
        except:
            print("Failed to copy....")
            raise 
            # quit()

def AnythingToRun():

        # print(args.modules)

        if args.modules == True:
            print("This is a module skipping CreateNEXFile()")
            return 

        if master != '':
          #  print(master)
            cmd = BASE_DIR+'/Emu/Cspect/Cspect.exe -w3 -16bit -brk -tv -vsync -nextrom -map='+head_tail[0]+'/'+filenamenoext+'.bas.map -zxnext -mmc='+head_tail[0]+'/data/ '+head_tail[0]+'/'+master
            p = subprocess.call(cmd, shell=True)

#def main():
# now scan the top 64 lines for any info on ORG/HEAP 
CheckForBasic()

ParseDirectives()

if args.runmaster == 0:
    # compile with zxbasic 

    ZXBCompile()

    # compiled ok, new lets generate a config to make a NEX file 

    ParseNEXCfg()

    # now use nexcreator.py to creat a NEX using the config file

    CreateNEXFile()

    # copy to destination if set

    CopyToDestination()

    timetaken = str(datetime.now()-start)
    print('Overall build time : '+timetaken[:-5]+'s')
    print('')

AnythingToRun()

if noemu == 0:
    sys.exit(0)
else:
    sys.exit(0)    
