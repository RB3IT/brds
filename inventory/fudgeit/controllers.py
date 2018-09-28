## Builtin
import datetime
import pathlib
import re
import traceback
## Builtin: gui
from tkinter import filedialog as tkfiledialog, messagebox as tkmessagebox
## Custom Module
from alcustoms.tkinter import advancedtkinter, smarttkinter
from alcustoms import sql, methods as almethods
## This Module
from BRDSolution.inventory.fudgeit import gui
## Parent Module
from BRDSolution.inventory import constants
## Sister Module
import BRDWebApp

class MainController(advancedtkinter.StackingManager):
    def __init__(self,parentpane, parent=None, eventmanager=None):
        super().__init__(parentpane=parentpane, parent = parent, eventmanager=eventmanager)
        self.eventmanager.bind("<<StackModified>>",self.checkreturn)

    def startup(self):
        self.loadsetup()

    def checkreturn(self,*event):
        if not self.stack:
            self.returntoparent()

    def returntoparent(self):
        ## There is no menu above this point at the moment, so it will fail
        p = self.parent
        self.cleanup()
        p.loadmenu()

    def loadsetup(self):
        con = SetupController(parent = self, parentpane = self.parentpane,eventmanager = self.eventmanager)
        self.addqueue(con)
        con.startup()

    def loadfudger(self,dbfile,dt):
        con = AdjustmentController(dbfile,dt,parent = self, parentpane = self.parentpane,eventmanager = self.eventmanager)
        self.addqueue(con)
        con.startup()

class SetupController(advancedtkinter.Controller):
    """ Controller that manages the Pane on which the database and month/year is selected """
    def __init__(self, pane = gui.SetupPane, **kw):
        super().__init__(pane=pane, **kw)

        p = self.pane
        p.databasefileentry.state(["readonly",])
        p.browsedatabasebutton.configure(command = self.browsefordatabase)
        p.continuebutton.configure(command = self.continuetoparent)
        p.cancelbutton.configure(command = self.canceltoparent)

        p.monthcombo.bind("<Return>",lambda e: self.continuetoparent())
        p.yearspinbox.bind("<Return>",lambda e: self.continuetoparent())

    def continuetoparent(self):
        """ Checks the database, month, and year and then returns the selections to the parent controller """
        p = self.pane
        dbfile = self.checkdbfile()
        if not dbfile: return
        try:
            dt = datetime.datetime(year = int(p.yearspinbox.get()), month = p.getmonth(), day = 1)
        except:
            traceback.print_exc()
            tkmessagebox.showerror("Invalid Month/Year", "Invalid Month/Year Combination")
            return
        conn = None
        conn = sql.connect(str(dbfile))
        try:
            items = conn.execute("""SELECT * FROM inventory WHERE date=:dt""",{'dt':dt.strftime(constants.DATEFORMAT)}).fetchall()
            if not items:
                tkmessagebox.showerror("No Inventory","Could not find inventory items for the given Month")
                return
        finally:
            if conn:
                conn.close()
        self.parent.loadfudger(dbfile,dt)

    def checkdbfile(self,dbfile = None):
        """ Validates the DB file """
        if dbfile is None:
            dbfile = self.pane.databasefileentry.get()
        dbfile = pathlib.Path(dbfile).resolve()
        if not dbfile.exists():
            tkmessagebox.showerror("Bad Database File","Selected Database does not exist")
            return
        conn = None
        try:
            conn = sql.connect(str(dbfile))
            tables = sql.getalltables(conn)
            if all(table in tables for table in ["inventory","items"]):
                tkmessagebox.showerror("Invalid Database","Database missing required tables")
                return
        except:
            traceback.print_exc()
            tkmessagebox.showerror("Invalid Database","Could not open target Database")
            return
        finally:
            if conn:
                conn.close()
        return dbfile

    def canceltoparent(self):
        """ Executes Cleanup """
        self.parent.dequeue(self)

    def browsefordatabase(self):
        """ Opens an Open File window to select the Database File """
        file = tkfiledialog.askopenfilename(filetypes=[('SQLite File','*.sqlite3'),],initialdir=BRDWebApp.ROOTDIR)
        if not file: return
        dbfile = self.checkdbfile(file)
        if not dbfile: return
        smarttkinter.setentry(self.pane.databasefileentry,file)

COSTRE = re.compile("""(?P<mod>[+-])?\$?(?P<value>.*)""")
def currency(number):
    """ Returns the American currency format of the number """
    return f"${number:0,.2f}"
class AdjustmentController(advancedtkinter.Controller):
    """ Controller for the Adjustment Pane. Sets, Calculates, and Adjusts Cost/Unit pricing for a Month of Inventory. """
    def __init__(self, dbfile, dt, pane = gui.AdjustmentPane, **kw):
        super().__init__(pane = pane, **kw)
        self.dbfile = dbfile
        self.dt = dt
        self.items = dict()

        p = self.pane
        p.targetentry.bind("<FocusOut>",self.prettyprinttarget)
        p.togglelockbutton.configure(command = self.lockcell)
        p.togglelockallbutton.configure(command = self.lockall)
        p.continuebutton.configure(command = self.submit)
        p.cancelbutton.configure(command = lambda: self.parent.dequeue(self))

        plugin = smarttkinter.ttk.SmartTreeviewEditCellPlugin(treeview = p.treeview, columns = ["Modified",],entry = gui.AdjustNumericEntry,  callback = self.updateitem) 


    def startup(self):
        """ Controller Startup

        Sets title, pulls inventory for the month, populates treeview, updates total.
        """
        p = self.pane

        p.titlelabel.configure(text=f"Inventory For: {self.dt.strftime('%B %Y')}")

        conn = sql.connect(str(self.dbfile))
        conn.row_factory = sql.dict_factory
        costs = conn.execute("""SELECT inventory.itemid, cost, price, vendor, inventory.*, items.description
        FROM inventory
        LEFT JOIN items ON inventory.itemid = items.itemid
        LEFT JOIN (
            SELECT itemid, cost, MAX(date) as latestdate, price, vendor
            FROM costs
            WHERE date <= :date2
            GROUP BY itemid) AS latestcosts ON inventory.itemid = latestcosts.itemid
        WHERE inventory.date = :date AND quantity > 0 AND quantity IS NOT NULL;
        """,
        dict(date = self.dt.strftime(constants.DATEFORMAT),date2 = self.dt)).fetchall()
        conn.close()

        for item in costs:
            item['date'] = self.dt
            item['newcost'] = item['cost']
        self.items = {item['itemid']: item for item in costs}
        for itemid in self.items:
            self.setitem(itemid)
        self.settotal()
        return super().startup()

    def submit(self):
        
        ## Only update in database costs that we explicitly changed
        updated = [item for itemid,item in self.items.items() if item['newcost'] != item['cost']]
        
        nextmonth = almethods.getfirstofnextmonthdatetime(self.dt)
        for item in updated: item['nextmonth'] = nextmonth
        conn = sql.connect(str(self.dbfile))

        ## Before updating, we need to make sure to preserve the cost on all other months
        ## This means making sure that each item has a "cost" value for next month that
        ## will supercede our arbitrary adjustment in the future
        try:
            import pprint
            pprint.pprint(updated)
            ## Make sure all updated items have a cost in the next month
            nextmonths = conn.executemany("""
            INSERT OR REPLACE INTO costs (id, itemid, date, cost, price, vendor)
            VALUES (
                (SELECT id FROM costs WHERE itemid = :itemid AND date = :nextmonth),
                :itemid,
                :nextmonth,
                :cost,
                :price,
                :vendor
                );
            """,updated)

            ## Add adjusted costs to database
            conn.executemany("""
            INSERT OR REPLACE INTO costs (id, itemid, date, cost, price, vendor)
            VALUES (
                (SELECT id FROM costs WHERE itemid = :itemid AND date = :date),
                :itemid,
                :date,
                :newcost,
                :price,
                :vendor
                );
            """, updated)
        except:
            tkmessagebox.showerror("An Error Occurred", traceback.format_exc())
            conn.rollback()
            return
        else:
            conn.commit()
        finally:
            conn.close()
        self.parent.cleanup()

    def setitem(self,itemid):
        item = self.items[itemid]
        try:
            self.pane.treeview.insert('', 'end', item['itemid'], values = (item['description'],item['quantity'],item['cost'],item['newcost'],f"{item['newcost'] * item['quantity']:.2f}"))
        except:
            traceback.print_exc()
            print(item)

    def updatetreeviewitem(self,itemid):
        item = self.items[itemid]
        try:
            self.pane.treeview.item(itemid, values = (item['description'],item['quantity'],item['cost'],item['newcost'],f"{item['newcost'] * item['quantity']:.2f}"))
        except:
            traceback.print_exc()

    def gettotal(self):
        """ Gets the inventory total amount """
        return round(sum([item['newcost'] * item['quantity'] for item in self.items.values()]),2)

    def settotal(self):
        """ Sets the Total Inventory Amount """
        total = self.gettotal()
        self.pane.totallabel.configure(text=currency(total))
        self.checktarget()

    def gettarget(self):
        """ Returns the target as a float """
        target = self.pane.targetentry.get()
        matches = re.findall("(\d|\.)",target)
        number = "".join(matches)
        if not number: number = 0
        return float(number)

    def prettyprinttarget(self,*event):
        """ Updates the target entry to look nice (and calls checktarget to boot)"""
        number = self.gettarget()
        smarttkinter.setentry(self.pane.targetentry,currency(number))
        self.checktarget()

    def checktarget(self):
        target = self.gettarget()
        total = self.gettotal()
        if target == total:
            self.pane.targetentry.configure(style="Valid.TEntry")
        else:
            self.pane.targetentry.configure(style="Invalid.TEntry")
        self.pane.differencelabel.configure(text = currency(total - target))

    def lockcell(self):
        """ Locks the currently selected cell """
        tree = self.pane.treeview
        sel = tree.selection()
        if not sel: return
        for cell in sel:
            if tree.tag_has(cell,'disabled'):
                tree.item(cell, tags = [])
            else:
                tree.item(cell, tags = ['disabled',])

    def lockall(self):
        """ Locks all cells """
        tree = self.pane.treeview
        ## Get unlocked cells
        unlocked = [cell for cell in tree.get_children() if not tree.tag_has(cell,'disabled')]
        ## If all cells are locked, toggle instead
        if not unlocked: unlocked = tree.get_children()
        tree.selection_set(unlocked)
        self.lockcell()

    def autocalculate(self):
        """ Runs autocalculation """

    def updateitem(self, itemid, column, newcost):
        """ Receives the SmartTreeviewEditCellPlugin event and updates the item price """
        research = COSTRE.search(newcost)
        if not research:
            tkmessagebox.showerror("Bad Edit Amount","Could not update cost")
            return
        mod,value = research.group("mod"),research.group('value')
        if not value: return
        value = float(value)
        if mod == "+": self.items[itemid]['newcost'] += value
        elif mod == "-": self.items[itemid]['newcost'] -= value
        else: self.items[itemid]['newcost'] = value
        self.items[itemid]['newcost'] = round(self.items[itemid]['newcost'],2)
        self.updatetreeviewitem(itemid)
        self.settotal()