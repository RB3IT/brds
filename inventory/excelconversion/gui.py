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

        ttk.Label(self,text="Quickbooks",style="Title.TLabel")

        self.costsbutton = ttk.Button(self,text="Costs")
        self.quantitiesbutton = ttk.Button(self,text="Inventory")

        self.cancelbutton = ttk.Button(self,text="Cancel")

        smarttkinter.masspack(self)

class SheetSelectPane(smarttkinter.GMMixin,smarttkinter.ttk.SmartFrame):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)

        ttk.Label(self,text="Worksheet Selection",style="Title.TLabel").pack()
        self.addworkbookbutton = ttk.Button(self,text="Add Workbook")
        self.addworkbookbutton.pack()

        self.worksheetselectionframe = ttk.LabelFrame(self,text="Workbooks")
        self.worksheetselectionframe.pack(fill='both',expand=True,padx=3,pady=10)

        bf = smarttkinter.ttk.SmartFrame(self)
        bf.pack()
        self.continuebutton = ttk.Button(bf,text='Continue')
        self.cancelbutton = ttk.Button(bf,text='Cancel')
        smarttkinter.masspack(bf,side='left')

class WorksheetSelectPane(smarttkinter.GMMixin,smarttkinter.ttk.SmartFrame):
    _gmkwargs=dict(fill='both',expand=True,padx=3,pady=3)
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)
        ## Used to lock out updateoptions to prevent recursion
        self.updateflag = False

        f = smarttkinter.ttk.SmartFrame(self)
        f.pack()
        self.removebutton = tk.Button(f,text="[X]")
        self.getworkbookbutton = ttk.Button(f,text="Workbook")
        self.workbookentry = ttk.Entry(f)
        smarttkinter.masspack(f,side='left')

        f= smarttkinter.ttk.SmartFrame(self)
        f.pack(fill='x')
        self.addworksheetbutton = ttk.Button(f,text="Add Worksheet")

        self.worksheetframe = ttk.LabelFrame(self,text="Worksheets")
        self.worksheetframe.pack(fill='both',expand=True,padx=3)

    def addworksheet(self,options,default=None):
        """ Adds a new Worksheet frame
        
        Adds a frame which contains:
            a button, which calls self.destroyworksheet
            a combobox (called worksheet) that has:
                "options" as values
                "default" selected (if not None)
                binds <<ComboboxSelected>> to self.updateoptions.
        Returns the Worksheet frame.
        """
        ## Memo, this could be replaced with an independent class, but I do not see the need for that at the moment
        f = smarttkinter.ttk.SmartFrame(self.worksheetframe)
        tk.Button(f,text="[X]",command = lambda: self.destroyworksheet(f))
        ttk.Label(f,text="Worksheet")
        f.worksheet = ttk.Combobox(f,values=options)
        f.worksheet.options = options
        f.worksheet.state(["readonly",])
        f.worksheet.bind("<<ComboboxSelected>>",self.updateoptions,"+")
        self.updateoptions()
        if default and (default is True or default in options):
            if default is True: default = options[0]
            f.worksheet.current(options.index(default))
        smarttkinter.masspack(f,side='left',padx=2)
        f.pack()
        self.updateoptions()
        return f

    def clearworksheets(self):
        for worksheet in self.worksheetframe.winfo_children():
            self.destroyworksheet(worksheet)

    def destroyworksheet(self,worksheetframe):
        worksheetframe.worksheet.options = None
        worksheetframe.destroy()
        self.updateoptions()

    def updateoptions(self,*event):
        """ Removes used options from worksheet combos """
        ## Using an updateflag in order to avoid triggering new updateoptions calls
        if self.updateflag: return
        self.updateflag = True
        ## Get all used options
        used = self.getallsheets()
        ## Pair combos with their current selection to make sure we don't remove it
        for value,worksheetframe in zip(used,self.worksheetframe.winfo_children()):
            worksheet = worksheetframe.worksheet
            ## Default options
            options = worksheet.options
            ## Options that aren't selected
            options = [option for option in options if option == value or option not in used]
            ## Update
            worksheet.configure(values = options)
            ## Restore proper selection
            if value:
                worksheet.current(options.index(value))

        self.updateflag = False

    def getallsheets(self):
        return [worksheetframe.worksheet.get() for worksheetframe in self.worksheetframe.winfo_children()]


class ImportPane(smarttkinter.GMMixin,smarttkinter.ttk.SmartFrame):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)


        ttk.Label(self,text="Results",style="Title.TLabel").pack()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both',expand=True)

        bf = smarttkinter.ttk.SmartFrame(self)
        bf.pack()
        self.continuebutton = ttk.Button(bf,text="Continue")
        self.cancelbutton = ttk.Button(bf,text="Cancel")
        smarttkinter.masspack(bf,side='left',padx=3)

class ExportPane(smarttkinter.GMMixin, smarttkinter.ttk.SmartFrame):
    def __init__(self,parent,**kw):
        super().__init__(parent, **kw)
        self.exportvar = tk.StringVar()

        ttk.Label(self, text="Export Options")

        f =smarttkinter.ttk.SmartFrame(self)
        self.csvradio = ttk.Radiobutton(f, text = "CSV", variable = self.exportvar, value = "csv", style = "Subtitle.TRadiobutton")
        ff = smarttkinter.ttk.SmartFrame(f)
        ttk.Label(ff, text = "Output File", style = "Bold.TLabel")
        self.csvbutton = ttk.Button(ff, text = "...")
        self.csventry = ttk.Entry(ff)
        smarttkinter.masspack(ff,side="left", padx = 2)
        smarttkinter.masspack(f)

        f = smarttkinter.ttk.SmartFrame(self)
        self.dbradio = ttk.Radiobutton(f, text = "Database", variable = self.exportvar, value = "db", style = "Subtitle.TRadiobutton")
        ff = smarttkinter.ttk.SmartFrame(f)
        ttk.Label(ff, text = "Database File", style = "Bold.TLabel")
        self.dbbutton = ttk.Button(ff, text = "...")
        self.dbentry = ttk.Entry(ff)
        smarttkinter.masspack(ff,side = "left", padx = 2)
        smarttkinter.masspack(f)

        bf = smarttkinter.ttk.SmartFrame(self)
        self.continuebutton = ttk.Button(bf, text = "Continue")
        self.cancelbutton = ttk.Button(bf, text = "Cancel")
        smarttkinter.masspack(bf, side="left", padx = 3)

        smarttkinter.masspack(self)