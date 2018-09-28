## Builtin:gui
import tkinter as tk, tkinter.ttk as ttk, tkinter.scrolledtext as tkscrolledtext
## Custom Module
from alcustoms.tkinter import advancedtkinter,smarttkinter

class GetFilesPane(smarttkinter.GMMixin,smarttkinter.ttk.SmartFrame):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)

        ttk.Label(self,text="Select Input Files",style='Title.TLabel')


        f = smarttkinter.ttk.SmartFrame(self)
        ttk.Label(f,text="Database",style='Bold.TLabel')
        self.databasebutton = ttk.Button(f,text="...")
        self.databaseentry = ttk.Entry(f)
        smarttkinter.masspack(f,side='left',padx=2)

        f = smarttkinter.ttk.SmartFrame(self)
        ttk.Label(f,text="Quickbooks Excel File",style='Bold.TLabel')
        self.quickbooksbutton = ttk.Button(f,text="...")
        self.quickbooksentry = ttk.Entry(f)
        smarttkinter.masspack(f,side='left',padx=2)

        f = smarttkinter.ttk.SmartFrame(self)
        ttk.Label(f,text="Output File",style='Bold.TLabel')
        self.outputbutton = ttk.Button(f,text="...")
        self.outputentry = ttk.Entry(f)
        smarttkinter.masspack(f,side='left',padx=2)

        bf = smarttkinter.ttk.SmartFrame(self)
        self.continuebutton = ttk.Button(bf,text="Continue")
        self.cancelbutton = ttk.Button(bf,text="Cancel")
        smarttkinter.masspack(bf,side='left',padx=3)

        smarttkinter.masspack(self)

class LoadConversionPane(smarttkinter.GMMixin,smarttkinter.ttk.SmartFrame):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)

        self.title = ttk.Label(self,style="Title.TLabel")
        self.output = tkscrolledtext.ScrolledText(self)

        self.continuebutton = ttk.Button(self,text="Continue")

        smarttkinter.masspack(self)

    def setmessage(self,title,message):
        self.title.configure(text=title)
        smarttkinter.setentry(self.output,message)