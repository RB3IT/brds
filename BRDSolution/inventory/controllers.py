"""
INVENTORY SHEET CONTROLLERS

"""

## Builtin
import itertools
import pathlib
import traceback
## Builtin: gui
import tkinter.filedialog as tkfiledialog, tkinter.messagebox as tkmessagebox
## Third Party
## Custom Module
from alcustoms.tkinter import advancedtkinter,smarttkinter
## This Module
from BRDSolution.inventory import gui
from BRDSolution.inventory.excelconversion import controllers as xlcontrollers
from BRDSolution.inventory.QuickBooks import controllers as qbcontrollers
from BRDSolution.inventory.fudgeit import controllers as fcontrollers


class MainController(advancedtkinter.StackingManager):
    def __init__(self,parentpane, parent=None, eventmanager=None):
        super().__init__(parentpane=parentpane, parent = parent, eventmanager=eventmanager)
        self.eventmanager.bind("<<StackModified>>",self.checkreturn)

    def startup(self):
        self.loadmenu()

    def checkreturn(self,*event):
        if not self.stack:
            self.returntoparent()

    def returntoparent(self):
        ## There is no menu above this point at the moment, so it will fail
        p = self.parent
        self.cleanup()
        p.loadmenu()

    def loadmenu(self):
        con = MenuController(parent = self, parentpane = self.parentpane,eventmanager = self.eventmanager)
        self.addqueue(con)
        con.startup()


class MenuController(advancedtkinter.Controller):
    def __init__(self,pane=gui.MenuPane,parent=None,parentpane=None,eventmanager = None):
        super().__init__(pane=pane,parent=parent,parentpane=parentpane,eventmanager=eventmanager)

        p = self.pane
        p.inventorybutton.configure(command = self.loadinventory)
        p.quickbooksbutton.configure(command = self.loadquickbooks)
        p.fudgeitbutton.configure(command = self.loadfudgeit)
        p.cancelbutton.configure(command = self.canceltoparent)

    def canceltoparent(self):
        self.parent.dequeue(self)

    def loadinventory(self):
        con = xlcontrollers.MainController(parent=self.parent,parentpane= self.parentpane)
        self.parent.addqueue(con)
        con.startup()

    def loadquickbooks(self):
        con = qbcontrollers.MainController(parent=self.parent,parentpane= self.parentpane)
        self.parent.addqueue(con)
        con.startup()

    def loadfudgeit(self):
        con = fcontrollers.MainController(parent=self.parent,parentpane= self.parentpane)
        self.parent.addqueue(con)
        con.startup()