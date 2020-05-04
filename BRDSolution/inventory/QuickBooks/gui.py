## Builtin: gui
import tkinter as tk, tkinter.ttk as ttk
## Custom Module
from alcustoms.tkinter import advancedtkinter,smarttkinter


class MenuPane(smarttkinter.GMMixin,smarttkinter.ttk.SmartFrame):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)

        ttk.Label(self,text="Quickbooks",style="Title.TLabel")

        self.costbutton = ttk.Button(self,text="Cost from Report")
        self.vendorbutton = ttk.Button(self,text="Vendor from Item List")

        self.cancelbutton = ttk.Button(self,text="Cancel")

        smarttkinter.masspack(self)