## Third Party
import xlrd
## This Module
from BRDSolution.inventory import constants

## NOTE: These objects are constructed from excel.classes.Item.todict(), which means that they're date attribute is already a DATEFORMAT string
####        This is probably the wrong thing to do and excel.classes.Item.todict() should probably return a datetime object still (as should these classes)

class Item():
    def __init__(self, itemid, include, itemindex, item, description, unitsize, location = None,**kw):
        self.itemid = itemid
        self.include = include
        self.itemindex = itemindex
        self.item = item
        self.description = description
        self.unitsize = unitsize
        self.location = None
    def __hash__(self):
        return hash(self.itemid)
    def __eq__(self,other):
        if isinstance(other,Item):
            return self.itemid == other.itemid
    def todict(self):
        """ Serializes the item to a mapping for output """
        return dict(itemid = self.itemid, include = self.include, itemindex = self.itemindex,
                    item = self.item, description = self.description, unitsize = self.unitsize,
                    location = self.location)

class ItemCost():
    def __init__(self,itemid,date,cost,price,**kw):
        self.itemid = itemid
        self.date = date
        self.cost = cost
        self.price = price
    def todict(self):
        """ Serializes the item to a mapping for output """
        return dict(itemid = self.itemid, date = "1900-01-01", cost = self.cost, price = self.price)
    def __eq__(self,other):
        if isinstance(other,ItemCost):
            return self.itemid == other.itemid
    def __hash__(self):
        return hash(self.itemid)

class InventoryItem():
    def __init__(self,itemid,date,quantity,**kw):
        self.itemid = itemid
        self.date = date
        self.quantity =quantity
    def todict(self):
        """ Serializes the item to a mapping for output """
        return dict(itemid = self.itemid, date = self.date, quantity = self.quantity)