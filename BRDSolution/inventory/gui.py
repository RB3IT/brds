"""
INVENTORY SHEET GUI

"""

## Builtin
## Builtin: gui
import tkinter as tk, tkinter.ttk as ttk
## Custom Module
from alcustoms.tkinter import smarttkinter


class MenuPane(smarttkinter.GMMixin,smarttkinter.ttk.SmartFrame):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)

        ttk.Label(self,text="Inventory",style="Title.TLabel")

        self.inventorybutton = ttk.Button(self,text="Import Inventory")
        self.quickbooksbutton = ttk.Button(self,text="Quickbooks Conversions")
        self.fudgeitbutton = ttk.Button(self,text="Fudge-it Module")

        self.cancelbutton = ttk.Button(self,text="Cancel")

        smarttkinter.masspack(self)

class ImportFrame(smarttkinter.ttk.SmartFrame):
    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)

        ttk.Label(self,text="Import Inventory", style = "Title.TLabel")