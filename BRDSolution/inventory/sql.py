## Builtin
import collections
import csv
import pathlib
## Custom Module
from alcustoms import decorators as aldecors
from alcustoms import sql
from alcustoms.sql.constants import *
## This Module
from BRDSolution.inventory import constants

"""
INVENTORY DATABASE

See Database Flowchart for arrangement
"""

def exportdb_to_csv(db,file):
    """ Exports the combined inventory tables to csv.
    
    db should be a InventoryDatabase object.
    file should be the target csv file (it will be overwritten if it already exists)
    """
    ## Replace the following once JointTables are functioning correctly
    values = db.execute("""SELECT *
    FROM inventory
    NATURAL JOIN items
    NATURAL JOIN costs""").fetchall()
    ## Consider rolling this into excelconversion.export_csv
    print(values[:10])
    with open(file,'w', newline = "") as f:
        writer = csv.DictWriter(f,fieldnames = constants.EXPORTHEADERS,extrasaction = 'ignore')
        writer.writeheader()
        writer.writerows(values)

def setupdatabase(file):
    """ Creates a new database at file location. Fails if file exists. """
    file = pathlib.Path(file).resolve()
    if file.exists():
        raise ValueError("File already exists")

    file.touch()
    db  = InventoryDatabase(file)

self_itemid_outputmatcher = aldecors.outputmatcher("itemid",self = True)

class InventoryBase(sql.DatabaseTable):
    @sql.connectiondecorator
    @sql.self_batchable
    @aldecors.self_one_in_one_out
    @sql.row_factory
    def getitembyid(self,*ids):
        """ Gets Items by item ID and returns inventory.Item objects (None for bad IDs). If only 1 ID is requested, will return the object itself. Delegates to self._getitembyID """
        return self._getitembyid(*ids)

    @self_itemid_outputmatcher
    def _getitembyid(self,*ids):
        """ The base function to get Items by item id. Returns the result of fetchall; missing ids return None instead of the default row_factory """
        selectstring = ", ".join("?" for _id in ids)
        sqlstring = f"""itemid in ({selectstring})"""
        ids = self.select(sqlstring = sqlstring, sqlreplacement = ids).fetchall()
        return ids

ITEMCOLUMNS = collections.OrderedDict(itemid=TEXT>>NOTNULL, include=BOOLEAN, itemindex=INT, item=TEXT, description=TEXT, unitsize = TEXT, location = TEXT)
ITEMPRIMARYKEY = [("itemid",),None]
class ItemTable(InventoryBase):
    def __init__(self, columns = ITEMCOLUMNS, foreignkeys = None, uniquekeys = None, primarykeys = ITEMPRIMARYKEY, name = "items", connection = None, rowfactory = None, **kw):
        return super().__init__(columns=columns, foreignkeys=foreignkeys, uniquekeys=uniquekeys, primarykeys=primarykeys, name=name, connection=connection, rowfactory=rowfactory, **kw)

    

## date is a Datetime
COSTSCOLUMNS = collections.OrderedDict(itemid=TEXT>>NOTNULL, date = TEXT, cost = DOUBLE, price = DOUBLE, vendor = TEXT)
COSTSFOREIGNKEYS = [("itemid","items","itemid"),]
COSTSUNIQUEKEYS = [
    (("itemid","date"),REPLACE)
    ]
class CostsTable(InventoryBase):
    def __init__(self, columns = COSTSCOLUMNS, primarykeys=None, foreignkeys = COSTSFOREIGNKEYS, uniquekeys = COSTSUNIQUEKEYS, name = "costs", connection = None, rowfactory = None, **kw):
        return super().__init__(columns=columns, foreignkeys=foreignkeys, uniquekeys=uniquekeys, primarykeys=primarykeys, name=name, connection=connection, rowfactory=rowfactory, **kw)

INVENTORYCOLUMNS = collections.OrderedDict(itemid=TEXT>>NOTNULL, date = TEXT, quantity = DOUBLE)
INVENTORYFOREIGNKEYS = [("itemid","items","itemid"),]
INVENTORYUNIQUEKEYS = [
    (("itemid","date"),REPLACE)
    ]
class InventoryTable(InventoryBase):
    def __init__(self, columns = INVENTORYCOLUMNS, primarykeys = None, foreignkeys = INVENTORYFOREIGNKEYS, uniquekeys = INVENTORYUNIQUEKEYS, name = "inventory", connection = None, rowfactory = None, **kw):
        return super().__init__(columns=columns, foreignkeys=foreignkeys, uniquekeys=uniquekeys, primarykeys=primarykeys, name=name, connection=connection, rowfactory=rowfactory, **kw)

INVENTORYTABLES = collections.OrderedDict(items=ItemTable, costs = CostsTable, inventory = InventoryTable)
class InventoryDatabase(sql.Database):
    def __init__(self, file = None, row_factory = sql.Row, tables = INVENTORYTABLES, jointtables = None, validate = True, check_same_thread = False, timeout = 10, **kw):
        return super().__init__(file=file, row_factory=row_factory, tables=tables, jointtables=jointtables, validate=validate, check_same_thread=check_same_thread, timeout=timeout, **kw)