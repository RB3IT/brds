## Builtin
import datetime
import pathlib
## Third Party
import openpyxl
## This module
from BRDSolution.inventory import constants

class AutoIncrementingDict(dict):
    def __init__(self,*args,**kw):
        self.lastint = 0
        return super().__init__(*args,  **kw)
    def __setitem__(self, key,value,**kwargs):
        if not isinstance(key,int): raise ValueError(f"{self.__class__.__name__} keys must be Integers")
        super().__setitem__(key,value,**kwargs)
    def append(self,value):
        self.lastint += 1
        self[self.lastint]=value

class ItemCost():
    def __init__(self, date,itemid,memo,vendor,cost,databaseid = None):
        self.date=date
        self.itemid = itemid
        self.memo = memo
        self.vendor = vendor
        self.cost = cost
        self.databaseid = databaseid
    def __eq__(self,other):
        if isinstance(other,ItemCost):
            return self.date == other.date and (self.itemid==other.itemid or self.databaseid == other.databaseid)
    def __hash__(self):
        return hash(f"{self.databaseid}-{self.date.strftime(constants.DATEFORMAT)}")

class Report():
    def __init__(self,file):
        self.file = pathlib.Path(file).resolve()
        if not self.file.exists():
            raise AttributeError("Report File does not exist")
        self.workbook = openpyxl.load_workbook(str(self.file),read_only=True)
        self.sheet = None
        self.items = AutoIncrementingDict()

        self.setworksheet(0)

    def setworksheet(self,sheet):
        if isinstance(sheet,str): self.sheet = self.workbook[sheet]
        elif isinstance(sheet,int): self.sheet = self.workbook.worksheets[sheet]
        else: raise ValueError("setworksheet argument must be string representing Worksheet Name or Integer representing Worksheet Index")
        self.items = AutoIncrementingDict()

        rows = list(self.sheet.rows)

        COLUMNNAMES = [cell.value for cell in rows[0]]
        DATE_INDEX = COLUMNNAMES.index("Date")
        ITEMID_INDEX = COLUMNNAMES.index("Item")
        MEMO_INDEX = COLUMNNAMES.index("Memo")
        VENDORNAME_INDEX = COLUMNNAMES.index("Source Name")
        COST_INDEX = COLUMNNAMES.index("Cost Price")

        for row in rows[1:]:
            cells = list(cell.value for cell in row)
            date = cells[DATE_INDEX]
            ## The Report has extra columns to Left of data dedicated to headers and such;
            ## Lines with headers will be blank in data area (so we're checking Date)
            if not date: continue
            itemid = cells[ITEMID_INDEX]
            ## Remove Parenthetical description
            ## e.g.- Rolling Doors:Springs:Spring4063 |-> (.406" x 3.75" OD x 20')
            itemid = itemid.rsplit("(")[0]
            ## Remove Heirarchical Item Info
            ## e.g.- Rolling Doors:Springs: <-| Spring4063
            itemid = itemid.rsplit(":",maxsplit=1)[-1].strip()
            memo = cells[MEMO_INDEX]
            vendor = cells[VENDORNAME_INDEX]
            cost = cells[COST_INDEX]
            self.items.append(ItemCost(date=date,itemid=itemid,memo=memo,vendor=vendor,cost=cost))

