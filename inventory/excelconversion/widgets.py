## Builtin: gui
import tkinter as tk, tkinter.ttk as ttk
## Custom Module
from alcustoms.tkinter import smarttkinter
## This Module
from BRDSolution.inventory.excelconversion import constants

class InventoryFrame(smarttkinter.GMMixin, smarttkinter.ttk.SmartFrame):
    def __init__(self,parent,inventory,**kw):
        super().__init__(parent,**kw)

        self.inventory = inventory
        self.headers = ["Description",]+[head for head in constants.MONTHINDICIES if head]

        self.titlelabel = ttk.Label(self,text=f"{inventory.monthname} {inventory.year}",style="Title.TLabel")
        self.titlelabel.pack()

        self.treeview = smarttkinter.ttk.SmartTreeview(self,columns = self.headers)
        self.treeview.pack(fill='both',expand=True)

        for item in inventory.itemtotals:
            values = [getattr(item,value.lower()) for value in self.headers]
            self.treeview.insert("",'end',item.itemid,values=values)

    def destroy(self):
        self.inventory = None
        super().destroy()