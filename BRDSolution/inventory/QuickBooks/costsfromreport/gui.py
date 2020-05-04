## Builtin:gui
import tkinter as tk, tkinter.ttk as ttk, tkinter.messagebox as tkmessagebox, tkinter.scrolledtext as tkscrolledtext
## Custom Module
from alcustoms.tkinter import advancedtkinter, smarttkinter

class GetFilesPane(smarttkinter.GMMixin,smarttkinter.ttk.SmartFrame):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)

        ttk.Label(self,text="Select Input Files",style='Title.TLabel')


        f = smarttkinter.ttk.SmartFrame(self)
        ttk.Label(f,text="Quickbooks Excel File",style='Bold.TLabel')
        self.quickbooksbutton = ttk.Button(f,text="...")
        self.quickbooksentry = ttk.Entry(f)
        smarttkinter.masspack(f,side='left',padx=2)

        f = smarttkinter.ttk.SmartFrame(self)
        ttk.Label(f,text="Database",style='Bold.TLabel')
        self.databasebutton = ttk.Button(f,text="...")
        self.databaseentry = ttk.Entry(f)
        smarttkinter.masspack(f,side='left',padx=2)

        bf = smarttkinter.ttk.SmartFrame(self)
        self.continuebutton = ttk.Button(bf,text="Continue")
        self.cancelbutton = ttk.Button(bf,text="Cancel")
        smarttkinter.masspack(bf,side='left',padx=3)

        smarttkinter.masspack(self)


class MissingPane(smarttkinter.GMMixin, smarttkinter.ttk.SmartFrame):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)

        ttk.Label(self,text="Items",style="Title.TLabel")
        ttk.Label(self,text="Items without a Database ID will not be included",style="Italics.Subtitle.TLabel")

        f = smarttkinter.ttk.SmartFrame(self)
        self.matchitembutton = ttk.Button(f,text="Find Selected")
        ttk.Label(f,text="Search:")
        self.searchvar = tk.StringVar()
        self.searchentry = ttk.Entry(f,textvariable= self.searchvar)
        self.searchentry.bind("<Escape>",lambda *event: smarttkinter.setentry(self.searchentry,""))
        smarttkinter.masspack(f,side='left',padx=3)

        self.treeview = smarttkinter.ttk.SmartTreeview(self,columns = ["Date","Item","Item Descript","DB ID"])

        bf = smarttkinter.ttk.SmartFrame(self)
        self.continuebutton = ttk.Button(bf,text="Continue")
        self.cancelbutton = ttk.Button(bf,text="Cancel")
        smarttkinter.masspack(bf,side='left',padx=3)

        smarttkinter.masspack(self)
        self.treeview.pack_configure(fill='both',expand = True)

@smarttkinter.popupdecorator
class MatchItemPopup(tk.Toplevel):
    def __init__(self,parent,itemid,item,table,**kw):
        super().__init__(parent,**kw)
        self.itemid=itemid
        self.item = item
        self.table=table
        self.result=None

        ttk.Label(self,text=f"Find Match for {item.itemid}",style="Subtitle.TLabel")
        ttk.Label(self,text=item.memo,style="Italics.TLabel")

        self.searchvar = tk.StringVar()
        self.searchvar.trace('w',self.search)
        self.searchentry = ttk.Entry(self,textvariable = self.searchvar)

        self.treeview = smarttkinter.ttk.SmartTreeview(self,columns=["ItemID","Description"])
        self.treeview.bind("<Double-Button-1>",self.getreturn)

        bf = smarttkinter.ttk.SmartFrame(self)
        self.continuebutton = ttk.Button(bf,text="Select",command=self.getreturn)
        self.cancelbutton = ttk.Button(bf,text="Cancel",command=self.returntoparent)
        smarttkinter.masspack(bf,side='left',padx=3)

        smarttkinter.masspack(self)
        self.treeview.pack_configure(fill='both',expand=True)

    def returntoparent(self):
        self.itemid = None
        self.table = None
        self.destroy()
        
    def getreturn(self,*event):
        sel = self.treeview.selection()
        if not sel:
            tkmessagebox.showerror("No Item Select","You have not selected a Database Item to match.")
            return
        self.result = sel[0]
        return self.returntoparent()

    def search(self,*event):
        value = self.searchvar.get().strip()
        results = self.table.advancedfilter(("OR",(
                                            ("COLUMN:itemid","LIKE",f"%{value}%"),
                                            ("COLUMN:description","LIKE",f"%{value}%")
                                        )
                                   ))
        self.treeview.clear()
        for item in results:
            self.treeview.insert('','end',item['itemid'],values=(item['itemid'],item['description']))

class ResultPane(smarttkinter.GMMixin,smarttkinter.ttk.SmartFrame):
    def __init__(self,parent,**kw):
        super().__init__(parent,**kw)

        self.notebook = ttk.Notebook(self)

        self.continuebutton  = ttk.Button(self,text="Continue")

        smarttkinter.masspack(self)

    def addmessage(self,tab,title,message):
        f = ttk.Frame(self.notebook)
        ttk.Label(f,text=title,style="Title.TLabel")

        infotext = tkscrolledtext.ScrolledText(f)
        infotext.insert(0.0,message)
        smarttkinter.masspack(f)
        infotext.pack_configure(fill='both',expand=True)

        self.notebook.add(f,text=tab)