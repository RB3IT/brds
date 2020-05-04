## Custom Module
from alcustoms.tkinter import advancedtkinter
## This Module
from BRDSolution.inventory.QuickBooks import gui
from BRDSolution.inventory.QuickBooks.costsfromreport import controllers as costscontrollers
from BRDSolution.inventory.QuickBooks.itemlistvendors import controllers as vendorcontrollers

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
        p.costbutton.configure(command = self.loadcost)
        p.vendorbutton.configure(command = self.loadvendor)
        p.cancelbutton.configure(command = self.canceltoparent)

    def canceltoparent(self):
        self.parent.dequeue(self)

    def loadcost(self):
        con = costscontrollers.MainController(parent=self.parent,parentpane= self.parentpane)
        self.parent.addqueue(con)
        con.startup()

    def loadvendor(self):
        con = vendorcontrollers.GetFilesController(parent=self.parent,parentpane= self.parentpane, eventmanager=self.eventmanager)
        self.parent.addqueue(con)
        con.startup()