## Custom: GUI
from alcustoms.tkinter import advancedtkinter as advtk, smarttkinter as smarttk
## Builtin: GUI
from tkinter import filedialog, messagebox
## Builtin
import csv
import pathlib
import re
## This Module
from . import gui
from . import excel
## Custom
from alcustoms import filemodules
from alcustoms.methods import DotVersion
from alcustoms.measurement import Imperial

class MenuController(advtk.Controller):
    def __init__(self, pane=gui.MenuPane, parent=None, parentpane=None, children=None, workers=None, eventmanager=None, destroypane='destroy', **kw):
        return super().__init__(pane=pane, parent=parent, parentpane=parentpane, children=children, workers=workers, eventmanager=eventmanager, destroypane=destroypane, **kw)
    
    def startup(self):
        p = self.pane
        p.gathercostingbutton.configure(command = lambda: self.parent.newchild(GatherCostingController))
        p.cancelbutton.configure(command = lambda: self.parent.dequeue(self))
        return super().startup()

class GatherCostingController(advtk.Controller):
    def __init__(self, pane=gui.GatherCostsPane, parent=None, parentpane=None, children=None, workers=None, eventmanager=None, destroypane='destroy', **kw):
        return super().__init__(pane=pane, parent=parent, parentpane=parentpane, children=children, workers=workers, eventmanager=eventmanager, destroypane=destroypane, **kw)

    def startup(self):
        p = self.pane
        p.getfolderbutton.configure(command = self.getfolder)
        p.getqbbutton.configure(command = self.getqb)
        p.getoutputbutton.configure(command = self.getoutput)
        p.continuebutton.configure(command = self.process)
        p.cancelbutton.configure(command = lambda: self.parent.dequeue(self))

    def getfolder(self):
        folder = filedialog.askdirectory(mustexist = True)
        if not folder: return
        folder = pathlib.Path(folder)
        if not folder.exists():
            messagebox.showerror("Invalid Folder", "Could not find folder")
            return
        smarttk.setentry(self.pane.folderentry,str(folder))

    def getqb(self):
        file = filedialog.askopenfilename(filetypes=[(".csv","CSV File"),])
        if not file: return
        file = pathlib.Path(file)
        if not file.exists():
            messagebox.showerror("Invalid File", "Could not find file")
            return
        if not file.suffix.lower() == ".csv":
            messagebox.showerror("Invalid File", "Incorrect file type: must be csv")
        smarttk.setentry(self.pane.qbentry,str(file))

    def getoutput(self):
        file = filedialog.asksaveasfilename(filetypes=[(".csv","CSV File"),])
        if not file: return
        file = pathlib.Path(file)
        if file.suffix.lower() != ".csv": file.suffix = file.with_suffix(".csv")
        smarttk.setentry(self.pane.outputentry,str(file))

    def process(self):
        ## Get Paths
        qbfile = pathlib.Path(self.pane.qbentry.get())
        inputfolder = pathlib.Path(self.pane.folderentry.get())
        outputfile = pathlib.Path(self.pane.outputentry.get())
        if outputfile.exists():
            if not outputfile.is_file():
                return messagebox.showerror("Invalid Output File",f"{outputfile} is not a valid file.")
            ask = messagebox.askyesno("Overwrite File", f"{outputfile.name} already exists: Overwrite it?")
            if not ask: return

        ## Parse QB Item List
        items = parseqb(qbfile)
        ## Get Active Rolling Door items
        doors = [item for item in items if item['Active Status'] == "Active" and "Rolling Door" in item['Item'] and "Rolling Steel Service Door" in item['Description']]
        ## Convert QB Item dicts inot Door Dicts
        processed = [processdoor(door) for door in doors]


        output = {}
        def organize_output(width: str, height: str)->dict:
            """ Checks the output dict to ensure the path for the given door exists, and returns the target dict.
           
                Ouput is nested dicts=> output[width][height] = dict()
                Returns the dict.
            """
            if width not in output: output[width] = {}
            if height not in output[width]: output[width][height] = {}
            return output[width][height]

        ## For each door, get the appropriate output dict, then sort by weatherseal
        for door in processed:
            outputdict = organize_output(str(door['width']), str(door['height']))

            if door['weatherseal']: name = "Full Weather Seal"
            else: name = ""
            outputdict[name] = door

        ## Gather Excel Sheets
        ## failures are unparsable Costing Sheets
        costingsheets, failures = excel.gathercostingsheets(inputfolder)

        if failures:
            ## Let user know there were unreadable Costing Sheets
            gui.FailurePopup(self.pane, failures)

        ## For each door, get the appropriate output dict and update the price
        ## Costing sheets don't have weatherseal yet
        for sheet in costingsheets:
            outputdict = organize_output(str(sheet.width), str(sheet.height))
            ## TODO: Costing Sheet Weatherseal
            name = ""
            if not outputdict.get(name):
                outputdict[name] = dict()
            ## TODO: When Weatherseal is updated for Costing Sheets,
            ##      make price = correct total
            outputdict[name]['price'] = sheet.totalbasecost

        ## Recollapse output
        out = []
        for w in output.values():
            for h in w.values():
                for ws in h.values(): out.append(ws)

        ## Output to CSV file
        with open(outputfile,'w', newline = "") as f:
            writer = csv.DictWriter(f, fieldnames = ["name","width","height","weatherseal","cost","price"])
            writer.writeheader()
            writer.writerows(out)

        ## Let user know the file was completed
        messagebox.showinfo("Complete",f"Your Pricing has completed at {outputfile}")

        ## Return to previous screen when done
        return self.parent.dequeue(self)

def parseqb(file: pathlib.Path)->list:
    """ Parses a QB Item list"""
    with open(file,'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def processdoor(door: dict)->dict:
    """ Takes a row from the item list and processes it into a dict containing door information """
    price = door['Price']
    cost = door['Cost']
    name = door['Description']
    width,height = None,None
    doorsize = DOORRE.search(name)
    if doorsize:
        width,height = Imperial(doorsize['width']),Imperial(doorsize['height'])
    weatherseal = "Full Weather Seal" in name
    return dict(price = price, cost = cost, name = name, width = width, height = height, weatherseal = weatherseal)

DOORRE = re.compile("(?P<width>\d+\s*\'\s*\d+\s*\").*?(?P<height>\d+\s*\'\s*\d+\s*\")")