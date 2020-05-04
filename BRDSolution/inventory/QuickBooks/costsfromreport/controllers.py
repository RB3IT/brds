## Builtin
import pathlib
import traceback
## Builtin: gui
import tkinter.filedialog as tkfiledialog, tkinter.messagebox as tkmessagebox
## Custom Module
from alcustoms.tkinter import advancedtkinter, smarttkinter
## This Module
from BRDSolution.inventory import constants, sql, methods as imethods
from BRDSolution.inventory.QuickBooks.costsfromreport import gui,classes,methods

class MainController(advancedtkinter.StackingManager):
    def __init__(self,parentpane, parent=None, eventmanager=None):
        super().__init__(parentpane=parentpane, parent = parent, eventmanager=eventmanager)
        self.eventmanager.bind("<<StackModified>>",self.checkreturn)

    def startup(self):
        con = GetFilesController(parent=self,parentpane= self.parentpane,eventmanager=self.eventmanager)
        self.addqueue(con)
        con.startup()

    def checkreturn(self,*event):
        if not self.stack:
            self.returntoparent()

    def returntoparent(self):
        self.parent.dequeue(self)

class GetFilesController(advancedtkinter.Controller):
    def __init__(self, pane=gui.GetFilesPane, parent=None, parentpane=None, eventmanager=None):
        super().__init__(pane=pane,parent=parent,parentpane=parentpane,eventmanager=eventmanager)

        p = self.pane
        p.databasebutton.configure(command = self.getdatabase)
        p.databaseentry.state(["disabled",])
        p.quickbooksbutton.configure(command = self.getquickbooks)
        p.quickbooksentry.state(["disabled",])

        p.continuebutton.configure(command = self.loadconversion)
        p.cancelbutton.configure(command = self.canceltoparent)

    def canceltoparent(self):
        self.parent.dequeue(self)

    def loadconversion(self):
        p = self.pane
        database,quickbooks = p.databaseentry.get().strip(), p.quickbooksentry.get().strip()
        if any(not file for file in [database,quickbooks,]):
            tkmessagebox.showerror('Missing File',"All fields are required. Please supply any missing files.")
            return
        con = MissingController(dict(database=database,quickbooks=quickbooks),parent=self.parent,parentpane=self.parentpane,eventmanager=self.eventmanager)
        self.parent.addqueue(con)
        con.startup()

    def getdatabase(self):
        file = tkfiledialog.askopenfilename(filetypes = (["Database",(".db",".sqlite3")],))
        if not file: return
        file = imethods.testfileintegrity(file)
        if not isinstance(file,pathlib.Path):
            tkmessagebox.showerror("Invalid File",f"Could not load file: please try loading another file. (error code: {file})")
        else:
            smarttkinter.setentry(self.pane.databaseentry,file)
    def getquickbooks(self):
        file = tkfiledialog.askopenfilename(filetypes = (["Excel File",(".xls",".xlsx")],))
        if not file: return
        file = imethods.testfileintegrity(file)
        if not isinstance(file,pathlib.Path):
            tkmessagebox.showerror("Invalid File",f"Could not load file: please try loading another file. (error code: {file})")
        else:
            smarttkinter.setentry(self.pane.quickbooksentry,file)



class MissingController(advancedtkinter.Controller):
    CLIPBOARDNONE = "<<__NONE__>>"
    def __init__(self,files,pane=gui.MissingPane,parent=None,parentpane=None,eventmanager=None):
        super().__init__(pane=pane,parent=parent,parentpane=parentpane,eventmanager=eventmanager)
        self.files = files
        self.clipboard = self.CLIPBOARDNONE

        p = self.pane
        p.matchitembutton.configure(command = self.openmatchdialog)
        p.searchvar.trace('w',self.filteritems)
        p.treeview.bind("<Double-Button-1>",self.openmatchdialog)
        p.treeview.bind("<Control-c>",self.copydatabaseid)
        p.treeview.bind("<Control-v>",self.pastedatabaseid)
        p.treeview.bind("<Delete>",self.cleardatabaseid)
        p.continuebutton.configure(command = self.loadresults)
        p.cancelbutton.configure(command = self.canceltoparent)

    def cleanup(self):
        self.files = None
        return super().cleanup()

    def startup(self):
        self.database = self.eventmanager.database = sql.InventoryDatabase(file=self.files['database'])
        self.itemstable = self.database.tables['items']
        self.report = classes.Report(self.files['quickbooks'])

        ## Find missing
        for key,item in self.report.items.items():
            itemid = item.itemid
            results = self.itemstable.filter(item={"=":itemid})
            ## If item is unambiguous
            if len(results) == 1:
                item.databaseid = results[0]['itemid']

        self.showallresults()

    def showallresults(self):
        self.pane.treeview.clear()
        self.loaditems(self.report.items)

    def loaditems(self,items):
        for key,item in items.items():
            self.pane.treeview.insert('',"end",key,values=(item.date.strftime("%m/%d/%Y"),item.itemid,item.memo,item.databaseid))
            
    def loadresults(self):
        databaseitems = [item for item in self.report.items.values() if item.databaseid]
        con = ExportController(databaseitems,parent=self.parent,parentpane = self.parentpane, eventmanager = self.eventmanager)
        self.parent.addqueue(con)
        con.startup()

    def canceltoparent(self):
        self.parent.dequeue(self)

    def openmatchdialog(self,*event):
        sel = self.pane.treeview.selection()
        if not sel:
            tkmessagebox.showerror("No Item Select","You have not selected a Database Item to match.")
            return
        sel = int(sel[0])
        item = self.report.items[sel]
        match = gui.MatchItemPopup(self.pane,sel,item,self.database.tables['items'])
        if not match: return
        return self.setitemmatch(sel,match)

    def setitemmatch(self,itemkey,databasematch):
        item = self.report.items[int(itemkey)]
        item.databaseid = databasematch
        self.pane.treeview.item(itemkey,values = (item.date.strftime("%m/%d/%Y"),item.itemid,item.memo,item.databaseid))

    def filteritems(self,*event):
        p = self.pane
        search = p.searchvar.get().strip().lower()
        if not search: self.showallresults()
        p.treeview.clear()
        results = {key:item for key,item in self.report.items.items() if search in "".join([str(item.itemid).lower(),str(item.memo).lower(),str(item.databaseid).lower()])}
        self.loaditems(results)

    def copydatabaseid(self,*event):
        key = self.pane.treeview.selection(count=1)
        if not key: self.clipboard = self.CLIPBOARDNONE
        else:
            item = self.report.items[int(key)]
            self.clipboard = item.databaseid

    def pastedatabaseid(self,*event):
        if self.clipboard == self.CLIPBOARDNONE: return
        sel = self.pane.treeview.selection()
        if not sel: return
        for key in sel:
            self.setitemmatch(key,self.clipboard)

    def cleardatabaseid(self,*event):
        key = self.pane.treeview.selection(count=1)
        if not key: return
        self.setitemmatch(key,None) 

class ExportController(advancedtkinter.Controller):
    def __init__(self,items,pane=gui.ResultPane,parent=None,parentpane=None,eventmanager=None):
        super().__init__(pane=pane,parent=parent,parentpane=parentpane,eventmanager=eventmanager)
        self.items = items

        p = self.pane
        p.continuebutton.configure(command = self.parent.returntoparent)

    def cleanup(self):
        self.items = None
        return super().cleanup()

    def startup(self):
        items = set(self.items)
        costtable = self.eventmanager.database.tables['costs']
        try:
            methods.exportitemstocsv('backup.csv',items)
        except: self.pane.addmessage("CSV Error","Secondary Save Failure",f"Failed to create csv backup of chanages.\n{traceback.format_exc()}")
        try:
            failures = methods.exportitemstodb(costtable,items)
            self.eventmanager.database.commit()
            self.eventmanager.database.close()
        except: self.pane.addmessage("DB Error","Database Backup Failure",f"Failed to commitchanges to database.\n{traceback.format_exc()}")
        else:
            if not failures:
                self.pane.addmessage("DB Result","Database Update Successful",f"Successfully Updated Database with {len(self.items)} Cost Items.")
            else:
                failuremessage = "\n".join(failures)
                self.pane.addmessage("DB Errors","Some Errors during Export",f"{len(items)-len(failures)} Items correctly exported; the rest had the following errors:\n{failuremessage}")
