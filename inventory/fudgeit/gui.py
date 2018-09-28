## Builtin
import calendar
import re
## Builtin: gui
import tkinter as tk, tkinter.ttk as ttk
## Custom Module
from alcustoms.tkinter import smarttkinter

class SetupPane(smarttkinter.ttk.SmartFrame, smarttkinter.GMMixin):
    def __init__(self,parent, **kw):
        super().__init__(parent, **kw)

        ttk.Label(self,text="Select Datbase and Month", style = "Subtitle.TLabel")

        f = smarttkinter.ttk.SmartFrame(self)
        ttk.Label(f,text="Database File",style="Bold.TLabel")
        self.browsedatabasebutton = ttk.Button(f,text="...")
        self.databasefileentry = ttk.Entry(f)
        smarttkinter.masspack(f,side='left')

        f = smarttkinter.ttk.SmartFrame(self)
        self.monthcombo = ttk.Combobox(f, values = list(calendar.month_name))
        self.yearspinbox = tk.Spinbox(f, from_=1970, to=2100)
        smarttkinter.masspack(f, side = 'left')

        bf = smarttkinter.ttk.SmartFrame(self)
        self.continuebutton = ttk.Button(bf,text="Continue")
        self.cancelbutton = ttk.Button(bf, text="Cancel")
        smarttkinter.masspack(bf,side='left',padx=3)

        smarttkinter.masspack(self)

    def getmonth(self):
        return self.monthcombo.current()

## NUMERICRE match non digits and period
NUMERICRE = re.compile("""
(                                   ## List of Bad things to check for
  [^\d.$,]                          ## Invalid Characters
| \.\d{3,}                          ## 3+ digit cents
| ^[^$]+\$                          ## Dollar sign not first character
| (?P<double>[\$\.]).*(?P=double)   ## Multiple Dollar signs, Decimals
| ,\d{,2}[.,]                       ## Trying to add delimeter after a comma and less-than 3 digits
| ,\d{4,}                           ## Incorrect length of separation when using commas
| (^|\D),                           ## Starting with a comma
)
""", re.VERBOSE)

"""
Some extra matches we're not using:
| ,(\d{,2}\D|\d{4,})    ## Incorrect comma separation (i.e.- 1,23,4567)
| (^|\D),               ## Comma without anything in front of it (i.e.- ,234.00)
"""

## Like NUMERICRE but also allows +/-
ADJUSTNUMERICRE = re.compile("""
(                                   ## List of Bad things to check for
  [^\d.$+-,]                        ## Invalid Characters
| \.\d{3,}                          ## 3+ digit cents
| ^[^\+\-\$]+[-+$]                  ## Dollar sign,+,- not first character when present
| (?P<double>[\$\.+-]).*(?P=double) ## Multiple Dollar signs, Decimals, +, -
| [+-].*[+-]                        ## Both + and -
| \$[+-]                            ## + or - after dollar sign
| ,\d{,2}[.,]                       ## Trying to add delimeter after a comma and less-than 3 digits
| ,\d{4,}                           ## Incorrect length of separation when using commas
| (^|\D),                           ## Starting with a comma
)
""", re.VERBOSE)

class AdjustNumericEntry(ttk.Entry):
    def __init__(self,parent, **kw):
        super().__init__(parent,**kw)
        self.callbackid = self.register(lambda text: not bool(ADJUSTNUMERICRE.search(text)))
        self.configure(validate = "key", validatecommand = (self.callbackid,"%P"))

class AdjustmentPane(smarttkinter.ttk.SmartFrame, smarttkinter.GMMixin):
    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)
        self.titlelabel = ttk.Label(self, style = "Title.TLabel")
        f = smarttkinter.ttk.SmartFrame(self)
        ttk.Label(f,text="Current Amount:", style = "Subtitle.TLabel").grid(row=0,column=0,sticky='w')
        self.totallabel = ttk.Label(f, style = "Subtitle.TLabel")
        self.totallabel.grid(row=0,column=1,sticky='e')
        ttk.Label(f, text="Target", style = "Subtitle.TLabel").grid(row=1,column=0,sticky='w')
        callback = self.register(lambda text: not bool(NUMERICRE.search(text)))
        self.targetentry = ttk.Entry(f, validate="key", validatecommand = (callback,'%P'))
        self.targetentry.grid(row=1,column=1,sticky='e')
        ttk.Label(f, text="Difference", style = "Subtitle.TLabel").grid(row = 2, column = 0, sticky = "w")
        self.differencelabel = ttk.Label(f, style = "Italics.Subtitile.TLabel")
        self.differencelabel.grid(row=2,column=1,sticky='e')

        f = smarttkinter.ttk.SmartFrame(self)
        self.togglelockbutton = ttk.Button(f, text="Lock Selected")
        self.togglelockallbutton = ttk.Button(f, text="Lock All")
        smarttkinter.masspack(f, side='left',padx=3)

        self.treeview = smarttkinter.ttk.SmartTreeview(self,columns = ['Item',"Quantity",'Original','Modified',"Subtotal"], plugins = [smarttkinter.ttk.SmartTreeviewDisablePlugin,])

        bf = smarttkinter.ttk.SmartFrame(self)
        self.continuebutton = ttk.Button(bf,text="Save")
        self.cancelbutton = ttk.Button(bf,text="Cancel")
        smarttkinter.masspack(bf,side='left',padx=3)

        smarttkinter.masspack(self)
        self.treeview.pack_configure(fill='both',expand = True)

