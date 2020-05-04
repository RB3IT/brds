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
from alcustoms import filemodules as alfilemodules
from alcustoms.tkinter import advancedtkinter,smarttkinter
## This Module
from BRDSolution.inventory.excelconversion import classes
from BRDSolution.inventory.excelconversion import gui
from BRDSolution.inventory.excelconversion import methods
from BRDSolution.inventory.excelconversion import widgets
from BRDSolution.inventory import sql

class MainController(advancedtkinter.StackingManager):
    def startup(self):
        con = MenuController(parentpane=self.parentpane,parent=self,eventmanager=self.eventmanager)
        self.addqueue(con)
        con.startup()

    def returntoparent(self):
        self.parent.dequeue(self)

class MenuController(advancedtkinter.Controller):
    def __init__(self,pane=gui.MenuPane,parent=None,parentpane=None,eventmanager = None):
        super().__init__(pane=pane,parent=parent,parentpane=parentpane,eventmanager=eventmanager)

        p = self.pane
        p.costsbutton.configure(command = self.loadcost)
        p.quantitiesbutton.configure(command = self.loadquantities)
        p.cancelbutton.configure(command = self.canceltoparent)

    def canceltoparent(self):
        self.parent.dequeue(self)

    def loadcost(self):
        con = CostsSheetSelectController(parent=self.parent,parentpane= self.parentpane, eventmanager = self.eventmanager)
        self.parent.addqueue(con)
        con.startup()

    def loadquantities(self):
        con = QuantitiesSheetSelectController(parent=self.parent,parentpane= self.parentpane, eventmanager=self.eventmanager)
        self.parent.addqueue(con)
        con.startup()

class SheetSelectController(advancedtkinter.Controller):
    def __init__(self, pane = gui.SheetSelectPane, parent = None, parentpane = None, children = None, workers = None, eventmanager = None, destroypane = 'destroy', **kw):
        super().__init__(pane=pane, parent=parent, parentpane=parentpane, children=children, workers=workers, eventmanager=eventmanager, destroypane=destroypane, **kw)

        p = self.pane
        p.addworkbookbutton.configure(command = self.addworkbook)
        p.continuebutton.configure(command = self.loadpage)
        p.cancelbutton.configure(command=self.canceltoparent)

    def startup(self):
        super().startup()
        self.addworkbook()

    def getinventories(self):
        sheets = itertools.chain.from_iterable([child.getallsheets() for child in self.children])
        inventories = []
        for sheet in sheets:
            inventories.extend(methods.parsesheet(sheet))
        ## Remove empty inventory lists
        inventories = [inventory for inventory in inventories if any(item.quantity for item in inventory.itemtotals)]
        inventories = methods.sortinventories(inventories)
        return inventories

    def canceltoparent(self):
        self.parent.dequeue(self)

    def addworkbook(self):
        con = self.addchildcontroller(WorksheetSelectController,parentpane = self.pane.worksheetselectionframe)
        con.show()

    def checkworkbook(self,workbook):
        """ Checks if workbook is already loaded """
        if any(child.workbook == workbook for child in self.children): return False
        return True
        
class CostsSheetSelectController(SheetSelectController):
    def loadpage(self):
        inventories = self.getinventories()
        con = CostsImportController(inventories = inventories, parentpane= self.parentpane,parent=self.parent,eventmanager=self.eventmanager)
        self.parent.addqueue(con)
        con.startup()

class QuantitiesSheetSelectController(SheetSelectController):
    def loadpage(self):
        inventories = self.getinventories()
        con = QuantitiesImportController(inventories = inventories, parentpane= self.parentpane,parent=self.parent,eventmanager=self.eventmanager)
        self.parent.addqueue(con)
        con.startup()

class WorksheetSelectController(advancedtkinter.Controller):
    """
    Controls a frame which contains a browse-for-file button and an entry that holds the file location.
    When a file is located, creates a subframe to select a worksheet; more worksheet frames can be added
    """
    def __init__(self,
                 pane = gui.WorksheetSelectPane, parent = None, parentpane = None, children = None, workers = None, eventmanager = None, destroypane = 'destroy', **kw):
        super().__init__(pane=pane, parent=parent, parentpane=parentpane, children=children, workers=workers, eventmanager=eventmanager, destroypane=destroypane, **kw)
        self.workbook = None

        p = self.pane
        p.workbookentry.state(["disabled",])
        p.removebutton.configure(command = self.cleanup)
        p.getworkbookbutton.configure(command = self.getworkbook)
        p.addworksheetbutton.configure(command = self.addworksheet)

    def getworkbook(self):
        """ Gets Workbook and then adds it via addworkbook """
        file = tkfiledialog.askopenfilename(filetypes = [("Excel Files",".xls*"),])
        if not file: return
        self.addworkbook(file)

    def addworksheet(self):
        self.pane.addworksheet(options=self.workbook.worksheets,default=True)

    def addworkbook(self,file):
        """ Validates a file and sets the workbookentry with its path """
        try:
            workbook = classes.Workbook(file)
        except:
            tkmessagebox.showerror("Bad File","Could not load the selected Workbook File: {file}")
            return
        if workbook == self.workbook: return
        if not self.parent.checkworkbook(workbook):
            tkmessagebox.showerror("Workbook Exists","Workbook is alread open; please use existing entry")
            return
        p = self.pane
        self.workbook = workbook
        smarttkinter.setentry(p.workbookentry,file)
        p.addworksheetbutton.pack(side='left')
        p.clearworksheets()
        self.addworksheet()

    def getallsheets(self):
        return [self.workbook.worksheet(sheet) for sheet in self.pane.getallsheets()]

class ImportController(advancedtkinter.Controller):
    """
    Currently functions as a confimation screen for the Inventory Import.

    Displays each excel sheet as a table within it's own tab and displays what information has been parsed.
    """
    def __init__(self, inventories = None,
                 pane = gui.ImportPane, parent = None, parentpane = None, children = None, workers = None, eventmanager = None, destroypane = 'destroy', **kw):
        super().__init__(pane=pane, parent=parent, parentpane=parentpane, children=children, workers=workers, eventmanager=eventmanager, destroypane=destroypane, **kw)
        self.inventories = inventories

        p = self.pane
        p.continuebutton.configure(command=self.loadoutput)
        p.cancelbutton.configure(command = self.cancel)

    def startup(self):
        for inventory in self.inventories:
            self.addinventory(inventory)

    def cancel(self):
        self.inventories = None
        self.parent.dequeue(self)

    def addinventory(self,inventory):
        note = self.pane.notebook
        widg = widgets.InventoryFrame(note,inventory)
        note.add(widg,text=f"{inventory.monthname} {inventory.year}")

class CostsImportController(ImportController):
    def loadoutput(self):
        con = CostsExportController(inventory = self.inventories,parent=self.parent,parentpane = self.parentpane, eventmanager = self.eventmanager)
        self.parent.addqueue(con)
        con.startup()

class QuantitiesImportController(ImportController):
    def loadoutput(self):
        con = QuantitiesExportController(inventory = self.inventories,parent=self.parent,parentpane = self.parentpane, eventmanager = self.eventmanager)
        self.parent.addqueue(con)
        con.startup()


class ExportController(advancedtkinter.Controller):
    """
    Allows user to select output format

    """
    def __init__(self, inventory= None,
                 pane = gui.ExportPane, parent = None, parentpane = None, children = None, workers = None, eventmanager = None, destroypane = 'destroy', **kw):
        super().__init__(pane=pane, parent=parent, parentpane=parentpane, children=children, workers=workers, eventmanager=eventmanager, destroypane=destroypane, **kw)
        inventory = itertools.chain.from_iterable(invent.itemtotals for invent in inventory)
        self.inventory = inventory

        p = self.pane
        self.toggleframes = [p.csvbutton,p.dbbutton]
        p.csventry.state(["disabled",])
        p.dbentry.state(["disabled",])

        p.csvbutton.configure(command = self.getfile)
        p.dbbutton.configure(command = self.getfile)
        p.exportvar.trace('w',self.updateexport)
        p.exportvar.set("csv")

        p.continuebutton.configure(command = self.exportandreturn)
        p.cancelbutton.configure(command = self.canceltoparent)

    def canceltoparent(self):
        self.inventory = None
        self.parent.dequeue(self)

    def export(self):
        """ Exports the information in the desired format """
        expo = self.pane.exportvar.get()
        if expo == "csv": return self.export_csv()
        elif expo == "db": return self.export_db()

    def exportandreturn(self):
        """ Exports the information and returns to the main menu """
        expo = self.export()
        if expo is False:
            tkmessagebox.showerror("Export Failure","Failed to export your data.")
        elif expo is None:
            return
        self.parent.returntoparent()

    def getfile(self):
        """ Gets the file name """
        ftype = self.pane.exportvar.get()
        if ftype == "csv":
            defaultextension = ".csv"
            filetypes = [("Comma-Separated",".csv"),]
        elif ftype == "db":
            defaultextension = ".db"
            filetypes = [("Database",(".db",".sqlite3"))]
        file = tkfiledialog.asksaveasfilename(defaultextension=defaultextension,
                                            filetypes=filetypes)
        if not file:
            tkmessagebox.showerror("No File","You did not select a filename to save as.")
            return
        if ftype == "csv": entry = self.pane.csventry
        elif ftype == "db": entry = self.pane.dbentry
        smarttkinter.setentry(entry,file)

    def updateexport(self,*event):
        """ Updates the gui to reflect currently selected export option """
        p = self.pane
        export = p.exportvar.get()

        if export == "csv":
            enable = [p.csvbutton,]
        elif export == "db":
            enable = [p.dbbutton,]

        for widget in self.toggleframes:
            if widget in enable: widget.state(["!disabled",])
            else: widget.state(["disabled",])


class CostsExportController(ExportController):
    def export_csv(self):
        """ Exports the data as Comma-Separated Values """
        file = self.pane.csventry.get()
        if not file:
            tkmessagebox.showerror("No File","You have not selected a filename to export to.")
            return None
        file = pathlib.Path(file).resolve()
        if file.exists():
            ask = tkmessagebox.askokcancel("File Exists","The file you selected already exists; would you like to overwrite it?")
            if not ask: return None
        try:
            inventorydicts = [item.todict() for item in self.inventory]
            methods.export_csv(inventorydicts,file)
        except Exception as e:
            smarttkinter.ErrorMessagebox("Export Failure","Failed to export Data",traceback.format_exc())
            return None
        tkmessagebox.showinfo("Export Success",f"Successfully Exported Inventory to CSV-file: {file}.")
        return True
            
    def export_db(self):
        """ Exports the data to a sqlite3 Database """
        file = self.pane.dbentry.get()
        if not file:
            tkmessagebox.showerror("No File","You have not selected a database to export to.")
            return None
        try:
            db = sql.InventoryDatabase(file = file)
            inventorydicts = [item.todict() for item in self.inventory]
            methods.export_db_costs(inventorydicts,db)
        except Exception as e:
            smarttkinter.ErrorMessagebox("Export Failure", "Failed to export Data",traceback.format_exc())
            db.rollback()
            return None
        else:
            db.commit()
            db.close()
        tkmessagebox.showinfo("Export Success",f"Successfully exported Inventory to database: {file}.")
        return True 


class QuantitiesExportController(ExportController):
    def export_csv(self):
        """ Exports the data as Comma-Separated Values """
        file = self.pane.csventry.get()
        if not file:
            tkmessagebox.showerror("No File","You have not selected a filename to export to.")
            return None
        file = pathlib.Path(file).resolve()
        if file.exists():
            ask = tkmessagebox.askokcancel("File Exists","The file you selected already exists; would you like to overwrite it?")
            if not ask: return None
        try:
            inventorydicts = [item.todict() for item in self.inventory]
            methods.export_csv(inventorydicts,file)
        except Exception as e:
            smarttkinter.ErrorMessagebox("Export Failure","Failed to export Data",traceback.format_exc())
            return None
        tkmessagebox.showinfo("Export Success",f"Successfully Exported Inventory to CSV-file: {file}.")
        return True
            
    def export_db(self):
        """ Exports the data to a sqlite3 Database """
        file = self.pane.dbentry.get()
        if not file:
            tkmessagebox.showerror("No File","You have not selected a database to export to.")
            return None
        try:
            db = sql.InventoryDatabase(file = file)
            inventorydicts = [item.todict() for item in self.inventory]
            errors = methods.export_db_quantities(inventorydicts,db)
        except Exception as e:
            smarttkinter.ErrorMessagebox("Export Failure", "Failed to export Data",traceback.format_exc())
            db.rollback()
            return None
        else:
            db.commit()
            db.close()

        if errors:
            smarttkinter.ErrorMessagebox("Export Failure", "Failed to export some data Data","\n".join([str(e) for e in errors]))
        else:
            tkmessagebox.showinfo("Export Success",f"Successfully exported Inventory to database: {file}.")
        return True 