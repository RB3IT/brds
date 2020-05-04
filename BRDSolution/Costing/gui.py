## Custom Module
from alcustoms.tkinter import smarttkinter as smarttk
## Builtin
import tkinter as tk
from tkinter import ttk
import winsound

class MenuPane(smarttk.Pane):
    def __init__(self, master, *args, **kw):
        super().__init__(master, *args, **kw)

        ttk.Label(self, text = "Costing Menu", style = "Title.TLabel")

        self.gathercostingbutton = ttk.Button(self, text = "Costing Gatherer", style = "Main.TButton")
        self.cancelbutton = ttk.Button(self, text = "Return")

        self.masspack()


class GatherCostsPane(smarttk.Pane):
    def __init__(self,parent,*args,**kw):
        super().__init__(parent,*args,**kw)

        f = smarttk.ttk.SmartFrame(self)
        ttk.Label(f, text = "Costing Folder", style = "Bold.TLabel")
        self.getfolderbutton = ttk.Button(f, text = "...")
        self.folderentry = ttk.Entry(f)
        self.folderentry.state(["readonly",])
        f.masspack(side='left',padx=2)

        f = smarttk.ttk.SmartFrame(self)
        ttk.Label(f, text = "Quickbooks Item List", style = "Bold.TLabel")
        self.getqbbutton = ttk.Button(f, text = "...")
        self.qbentry = ttk.Entry(f)
        self.qbentry.state(["readonly",])
        f.masspack(side='left',padx=2)

        f = smarttk.ttk.SmartFrame(self)
        ttk.Label(f, text = "Output File", style = "Bold.TLabel")
        self.getoutputbutton = ttk.Button(f, text = "...")
        self.outputentry = ttk.Entry(f)
        self.outputentry.state(["readonly",])
        f.masspack(side='left',padx=2)

        bf = smarttk.ttk.SmartFrame(self)
        self.continuebutton = ttk.Button(bf, text = "Continue")
        self.cancelbutton = ttk.Button(bf, text = "Back")
        bf.masspack(side='left', padx = 2)

        self.masspack()

@smarttk.modulardecorator
def FailurePopup(parent, failures):

    def setclipboard():
        """ Copies failures to clipboard """
        p.clipboard_clear()
        p.clipboard_append("\n".join([str(file) for file in failures]))
        p.update()
        winsound.MessageBeep()

    p = popup = tk.Toplevel(parent)
    f = smarttk.ttk.SmartFrame(p)
    ttk.Label(f, text =
"""Could Not Read the following Costing sheets:
  Update them to the most recent version.""", style = "Bold.TLabel")
    lb = smarttk.ScrolledWidget(f, tk.Listbox)
    lb.insert('end',*[file.name for file in failures])

    bf = smarttk.ttk.SmartFrame(f)
    ttk.Button(bf, text = "Copy to Clipboard", command = setclipboard)
    ttk.Button(bf, text = "Continue", command = p.destroy)
    bf.masspack()

    f.masspack()
    f.pack()
    return p