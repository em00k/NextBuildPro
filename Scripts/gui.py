
from tkinter import *
from tkinter.ttk import Progressbar
from tkinter.ttk import Combobox
from tkinter.ttk import Notebook
from tkinter import ttk
import tkinter.font

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
        self.buttonlaunch = Button(self.w1, text = "Build and Launch", bg = "#414141", fg = "#c0c0c0", font = tkinter.font.Font(family = "MS Shell Dlg 2", size = 8), cursor = "arrow", state = "normal")
        self.buttonlaunch.place(x = 50, y = 50, width = 130, height = 32)
        self.buttonlaunch.focus_set()
        self.buttonlaunch['command'] = self.BuildModules
        self.label1 = Label(self.w1, text = "Build module and launch in CSpect [Return]", bg = "#414141", fg = "#c0c0c0", font = tkinter.font.Font(family = "MS Shell Dlg 2", size = 8), cursor = "arrow", state = "normal")
        self.label1.place(x = 200, y = 44, width = 260, height = 42)
        self.buttonall = Button(self.w1, text = "Build All Modules", bg = "#414141", fg = "#c0c0c0", font = tkinter.font.Font(family = "MS Shell Dlg 2", size = 8), cursor = "arrow", state = "normal")
        self.buttonall.place(x = 50, y = 90, width = 130, height = 32)
        self.buttonall['command'] = self.BuildAll
        self.label2 = Label(self.w1, text = "NextbBuild8", font = tkinter.font.Font(family = "MS Shell Dlg 2", size = 8), cursor = "arrow", state = "normal")
        self.label2.place(x = 430, y = 180, width = 80, height = 22)
        self.buttonconfig = Button(self.w1, text = "Configuration [e]", bg = "#414141", fg = "#c0c0c0", font = tkinter.font.Font(family = "MS Shell Dlg 2", size = 8), cursor = "arrow", state = "normal")
        self.buttonconfig.place(x = 50, y = 130, width = 130, height = 32)
        self.buttonconfig['command'] = self.EditConfig

    def BuildModules(self):
        print('BuildModules')
        Quit(1)

    def BuildAll(self):
        print('BuildAll')

    def EditConfig(self):
        print('EditConfig')


def Quit(e):
    a.w1.destroy()


if __name__ == '__main__':
    a = Widget1(0)
    center(a.w1)
    a.w1.bind("<Escape>", Quit)
    a.w1.bind("<Return>", Widget1.BuildModules)
    a.w1.iconphoto(False, tkinter.PhotoImage(file='./imgs/nextbuild.png'))
    a.buttonlaunch.focus_set()
    a.w1.mainloop()
