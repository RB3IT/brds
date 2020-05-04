## Builtin
import datetime
import pathlib
## Third Party
import xlrd
## THis Module
from BRDSolution.inventory import constants

def getdatetime(date):
    """ Gets and Validates the initial datetime object for Inventory and ItemInventory """
    if isinstance(date,str):
            date = datetime.datetime.strptime(date,constants.DATEFORMAT).date()
    if not isinstance(date,(datetime.date,datetime.datetime)):
        raise AttributeError(f"date attribute must be string (representing date {constants.DATEFORMAT}) or datetime instance.")
    return date

class Workbook():
    def __init__(self,file):
        self.file = pathlib.Path(file).resolve()
        if not self.file.exists():
            raise AttributeError("Filepath must exist!")
        self.workbook = xlrd.open_workbook(str(self.file))
    @property
    def worksheets(self):
        return self.workbook.sheet_names()
    def worksheet(self,sheetname):
        return self.workbook.sheet_by_name(sheetname)
    def __eq__(self,other):
        if isinstance(other,Workbook):
            return str(self.file) == str(other.file)

class Inventory():
    """ A container for a month's inventory list.
    
    Maintains the datetime object for the Inventory list and
    sets all item added to that object.
    """
    _date = datetime.date(year=1990,month=1,day=1)
    itemtotals = None
    def __init__(self,date,itemtotals = list()):
        self.itemtotals = list()

        date = getdatetime(date)
        self.date = date

        self.additemtotals(*itemtotals)

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self,month=None,year=None):
        """ The Setter for the Inventory's date attribute (which is a datetime object)

        Accepts either a month and/or year, or a datetime as a positional argument.
        If month is supplied, month should be an integer between 1 and 12 inclusive.
        If year is supplied, it should be an integer greater than 0.
        If one positional argument is passed, it should be a datetime, and both month
        and year will be set based on it.
        """
        if month is None and year is None: return
        if isinstance(month,(datetime.date,datetime.datetime)):
            year = month.year
            month = month.month
        if month:
            if month not in range(1,13):
                raise AttributeError("Month must be in [1...12] inclusive")
            self._date = self._date.replace(month = month)
        if year:
            if year <= 0:
                raise AttributeError("Year must be greater than 0")
            self._date = self._date.replace(year = year)

    @property
    def monthname(self):
        return self.date.strftime("%B")

    @property
    def month(self):
        return self.date.month

    @property
    def year(self):
        return self.date.year

    def additemtotals(self,*itemtotals):
        """ Adds InventoryItems or dicts representing Inventoryitems to the Inventory

        Updates the values to reflect the Inventory's month and year
        """
        badvalues = [item for item in itemtotals if not isinstance(item,(dict,InventoryItem))]
        if badvalues:
            raise ValueError("itemtotals must be a list of dicts and or InventoryItem")
        itemdicts = [item for item in itemtotals if isinstance(item,dict)]
        for item in itemdicts:
            item['date'] = self.date
        itemtotals = [item for item in itemtotals if item not in itemdicts]
        itemdicts = [InventoryItem(**item) for item in itemdicts]
        
        self.itemtotals+= itemtotals + itemdicts

    def todicts(self):
        """ Converts items to dictionaries """
        return [item.todict() for item in self.itemtotals]

class InventoryItem():
    """ A full representation of a single month's accounting information for a particular item. """
    def __init__(self,itemid, include, itemindex, item, description, date, cost, price,quantity,total = None, unitsize = None):
        """ Creates a new InventoryItem object.
        
        Total is accepted as a paramater for compatibility reasons; the InventoryItem
        has its own total attribute that is generated from the cost and quantity.
        """
        self.itemid = itemid
        if not include: include = False
        self.include = bool(include)
        self.itemindex = itemindex
        self.item = item
        self.description = description
        self.unitsize = unitsize
        date = getdatetime(date)
        self.date = date
        if not cost: self.cost = None
        else: self.cost = float(cost)
        if not price: self.price = None
        else: self.price = float(price)
        if not quantity: self.quantity = None
        else: self.quantity = float(quantity)
    @property
    def total(self):
        """ Returns the total cost of the item for the month based on its quantity """
        cost,quantity = self.cost,self.quantity
        if not cost: cost = 0
        if not quantity: quantity = 0
        return cost * quantity
    def todict(self):
        """ Serializes the InventoryItem (used for output) """
        return dict(itemid = self.itemid, include = self.include, itemindex = self.itemindex,
                    item = self.item, description = self.description, unitsize = self.unitsize,
                    date = self.date.strftime(constants.DATEFORMAT), cost = self.cost, price = self.price,
                    quantity = self.quantity)