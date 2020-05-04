## Builtin
import pathlib
import traceback
## Builtin: gui
from tkinter import messagebox as tkmessagebox, filedialog as tkfiledialog
## Custom Module
from alcustoms.tkinter import advancedtkinter,smarttkinter
## This Module
from BRDSolution.inventory import methods as imethods
from BRDSolution.inventory.QuickBooks.itemlistvendors import gui
from BRDSolution.inventory.QuickBooks.itemlistvendors import methods

class GetFilesController(advancedtkinter.Controller):
    def __init__(self, pane=gui.GetFilesPane, parent=None, parentpane=None, eventmanager=None):
        super().__init__(pane=pane,parent=parent,parentpane=parentpane,eventmanager=eventmanager)

        p = self.pane
        p.databasebutton.configure(command = self.getdatabase)
        p.databaseentry.state(["disabled",])
        p.quickbooksbutton.configure(command = self.getquickbooks)
        p.quickbooksentry.state(["disabled",])
        p.outputbutton.configure(command = self.getoutput)
        p.outputentry.state(["disabled",])

        p.continuebutton.configure(command = self.loadconversion)
        p.cancelbutton.configure(command = self.canceltoparent)

    def canceltoparent(self):
        self.parent.dequeue(self)

    def loadconversion(self):
        p = self.pane
        database,quickbooks,output = p.databaseentry.get().strip(), p.quickbooksentry.get().strip(), p.outputentry.get().strip()
        if any(not file for file in [database,quickbooks,output]):
            tkmessagebox.showerror('Missing File',"All fields are required. Please supply any missing files.")
            return
        con = LoadConversionController(dict(database=database,quickbooks=quickbooks,output=output),parent=self.parent,parentpane=self.parentpane,eventmanager=self.eventmanager)
        self.parent.addqueue(con)

    def getdatabase(self):
        file = tkfiledialog.askopenfilename(filetypes = (["Database",(".db",".sqlite3")],))
        file = imethods.testfileintegrity(file)
        if not isinstance(file,pathlib.Path):
            tkmessagebox.showerror("Invalid File",f"Could not load file: please try loading another file. (error code: {file})")
        smarttkinter.setentry(self.pane.databaseentry,file)
    def getquickbooks(self):
        file = tkfiledialog.askopenfilename(filetypes = (["Excel File",(".xls",".xlsx")],))
        file = imethods.testfileintegrity(file)
        if not isinstance(file,pathlib.Path):
            tkmessagebox.showerror("Invalid File",f"Could not load file: please try loading another file. (error code: {file})")
        smarttkinter.setentry(self.pane.quickbooksentry,file)
    def getoutput(self):
        file = tkfiledialog.asksaveasfilename(filetypes = (["Comma-separated Values",".csv"],),defaultextension=".csv")
        smarttkinter.setentry(self.pane.outputentry,file)

class LoadConversionController(advancedtkinter.Controller):
    def __init__(self, files, pane=gui.LoadConversionPane, parent=None, parentpane=None, eventmanager=None):
        super().__init__(pane=pane,parent=parent,parentpane=parentpane,eventmanager=eventmanager)
        self.files = files

        self.pane.continuebutton.configure(command=self.parent.returntoparent)
        self.startup()

    def startup(self):
        start = super().startup()
        try:
            output = methods.generatequickbooksexcelconversion(self.files['database'],self.files['quickbooks'])
            methods.exportconversionresults(output,self.files['output'])
        except:
            self.pane.setmessage('Failed to Convert',f'Could not convert information from Quickbook Excel Output:\n{traceback.format_exc()}')
        else:
            self.pane.setmessage("Conversion Successful",f"Successfully converted Quickbooks output! Your file is available at:\n{self.files['output']}")
