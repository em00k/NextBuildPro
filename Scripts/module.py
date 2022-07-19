#!/usr/bin/env python3
#
# Compiles modules*.bas in the Sourcs\xx folder then copies the Module*.bin to the \data\
# Thanks to D for his help :)

import sys
import subprocess, os, platform
import time
import glob
import shutil 

from tkinter import *
from tkinter.ttk import Progressbar
from tkinter.ttk import Combobox
from tkinter.ttk import Notebook
from tkinter import ttk
import tkinter.font

global inputfilea, BASE_DIR 

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
SCRIPTS_DIR = os.path.abspath(os.path.join(BASE_DIR, 'Scripts'))  # ZX BASIC root path



#from nextbuild import ProcessDirective 

inputfilea = sys.argv[1]                         
head_tail = os.path.split(inputfilea)            # get the path of the file 
sys.path.append(head_tail[0])                   # add to paths 


def ProcessModules():
    print("Compiling Modules ")
    print("Base Dir : "+BASE_DIR)
    print("Main Source : "+inputfilea)
    ## WINDOWS
    #tmp_ath = head_tail[0]+'\\Module*.bas'
    ## MACOS
    tmp_ath = head_tail[0]+'/Module*.bas'
    print("Looking for Modules : "+tmp_ath)
    # print(glob.glob("*.*"))
    print("")

    for file in glob.glob(tmp_ath):
        print("Creating module : "+file)
        try:
            ## WINDOWS
            cmd = BASE_DIR+'/zxbasic/python/python.exe '+BASE_DIR+'/scripts/nextbuild.py -b '+file+' -q -m'
            ## MACOS
            #cmd = '/usr/local/bin/python3 '+BASE_DIR+'/scripts/nextbuild.py -b '+file
            # print(cmd)
            p = subprocess.call(cmd, shell=True)
            lastfile = file 
            # run once more but do not compile. 
        except:
            raise 
            
    print("Copying modules to data folder...")
    tmp_ath = head_tail[0]+'\\Module*.bin'
    for file in glob.glob(tmp_ath):
        print('Copy : '+file+" > "+head_tail[0]+'\\data\\')
        shutil.copy(file, head_tail[0]+'\\data\\')

    print("Done.")            

        
    cmd = BASE_DIR+'/zxbasic/python/python.exe '+BASE_DIR+'/scripts/nextbuild.py -b '+lastfile+' -q -l'

    p = subprocess.call(cmd, shell=True)


def center(win):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

class Widget1():
    def __init__(self, parent):
        self.gui(parent)

    def gui(self, parent):
        if parent == 0:
            self.w1 = Tk()
            self.w1.configure(bg = '#414141')
            self.w1.geometry('500x200')
            self.w1.title('NextBuildv8')
        else:
            self.w1 = Frame(parent)
            self.w1.configure(bg = '#414141')
            self.w1.place(x = 0, y = 0, width = 500, height = 200)
        self.buttonlaunch = Button(self.w1, text = "Build and Launch [F5]", bg = "#414141", fg = "#c0c0c0", font = tkinter.font.Font(family = "MS Shell Dlg 2", size = 8), cursor = "arrow", state = "normal")
        self.buttonlaunch.place(x = 50, y = 50, width = 130, height = 32)
        self.buttonlaunch.focus_set()
        self.buttonlaunch['command'] = self.BuildModule
        self.label1 = Label(self.w1, text = "Build module and launch in CSpect [Return]", bg = "#414141", fg = "#c0c0c0", font = tkinter.font.Font(family = "MS Shell Dlg 2", size = 8), cursor = "arrow", state = "normal")
        self.label1.place(x = 200, y = 44, width = 260, height = 42)
        self.buttonall = Button(self.w1, text = "Build All Modules [F6]", bg = "#414141", fg = "#c0c0c0", font = tkinter.font.Font(family = "MS Shell Dlg 2", size = 8), cursor = "arrow", state = "normal")
        
        self.buttonall.place(x = 50, y = 90, width = 130, height = 32)
        self.buttonall['command'] = self.BuildAll
        
        self.label3 = Label(self.w1, text = "Build all modules and run main Nex", bg = "#414141", fg = "#c0c0c0", font = tkinter.font.Font(family = "MS Shell Dlg 2", size = 8), cursor = "arrow", state = "normal")
        self.label3.place(x = 200, y = 84, width = 260, height = 42)

        self.label2 = Label(self.w1, text = "NextbBuild8", font = tkinter.font.Font(family = "MS Shell Dlg 2", size = 8), cursor = "arrow", state = "normal")
        self.label2.place(x = 430, y = 180, width = 80, height = 22)
        self.buttonconfig = Button(self.w1, text = "Configuration [e]", bg = "#414141", fg = "#c0c0c0", font = tkinter.font.Font(family = "MS Shell Dlg 2", size = 8), cursor = "arrow", state = "normal")
        self.buttonconfig.place(x = 50, y = 130, width = 130, height = 32)
        self.buttonconfig['command'] = self.EditConfig

    def BuildModule(self):
        print('BuildModule')
        Quit(1)
        SingleCompile(0)
        sys.exit(0)

    def BuildAll(self):
        print('BuildAll')
        Quit(1)
        ProcessModules()
        sys.exit(0)

    def EditConfig(self):
        print('EditConfig')


def Quit(e):
    a.w1.destroy()

def SingleCompile(e):
    # compile current source and run 
    
    cmd = BASE_DIR+'/zxbasic/python/python.exe '+BASE_DIR+'/scripts/nextbuild.py -b '+inputfilea+' -s'

    p = subprocess.call(cmd, shell=True)
    
    
def RunLastNext(e):
    # compile current source and run 
    
    cmd = BASE_DIR+'/zxbasic/python/python.exe '+BASE_DIR+'/scripts/nextbuild.py -b '+inputfilea+' -l'

    p = subprocess.call(cmd, shell=True)

if __name__ == '__main__':
    
    a = Widget1(0)
    center(a.w1)
    a.w1.bind("<Escape>", Quit)
    a.w1.bind("<F5>", Widget1.BuildModule)
    a.w1.bind("<Return>", Widget1.BuildModule)
    a.w1.bind("<F6>", Widget1.BuildAll)
    a.w1.bind("<F7>", RunLastNext)
    a.w1.iconphoto(False, tkinter.PhotoImage(file=BASE_DIR+'\\Scripts\\imgs\\nextbuild.png'))
    a.buttonlaunch.focus_set()
    a.w1.mainloop()