## Builtin
import calendar
import csv
import datetime
import re
## This Module
from BRDSolution.inventory.excelconversion import classes
from BRDSolution.inventory.excelconversion import constants
from BRDSolution.inventory import classes as iclasses
from BRDSolution.inventory import constants as iconstants
from BRDSolution.inventory import sql

MONTHCAPTURE = re.compile("""(?P<month>\w+)\s+(?P<day>\d+),?\s+(?P<year>\d+)""")

MONTHLOOKUP = dict((v,k) for k,v in enumerate(calendar.month_name))

def parsesheet(sheet):
    """ Parses an inventory sheet into individual, monthly inventories """
    output = []

    stats = list(enumerate(constants.XLCOLUMNINDICIES))
    ## [2:] reflects header row
    cols = [sheet.col(i)[2:] for i,head in stats if head]
    itemdefs = list(zip(*cols))

    headers = [head.lower() for head in constants.XLCOLUMNINDICIES if head]
    itemdefs = [dict(list(zip(headers,[cell.value for cell in item]))) for item in itemdefs]
    #itemdefs = [item for item in itemdefs if item['Include']]
    for item in itemdefs:
        try: itemindex=float(item['itemindex'])
        except: itemindex = item['itemindex']
        item['itemid'] = f"{itemindex}-{item['item']}"

    cols = sheet.ncols
    index = len(constants.XLCOLUMNINDICIES)-1

    monthheaders = constants.MONTHINDICIES
    valueheaders = [head.lower() for head in constants.MONTHINDICIES if head]
    dtindex = constants.MONTHHEADERS.index("MonthYear")
    headersindex = constants.MONTHHEADERS.index("Headers")

    while index < cols-len(monthheaders):
        ## Identify Start of range
        index+=1
        ## Get headers
        headers = [sheet.cell(headersindex,i).value for i in range(index,index+len(constants.MONTHINDICIES))]
        ## If headers don't match predicted headers, continue from next index
        if headers != monthheaders: continue

        ## Get Month/Year
        ## Get value from top row of range
        dt = [sheet.cell(dtindex,i).value for i in range(index,index+len(monthheaders)) if sheet.cell(dtindex,i).value][0]
        dt = MONTHCAPTURE.search(dt)
        ## If regex doesn't match, continue from next batch of indices
        if not dt:
            index += len(monthheaders)-1
            continue
        month,year = dt.group('month'),dt.group('year')
        month = list(calendar.month_name).index(month)
        date = datetime.date(year = int(year),month = month, day = 1)

        ## Get values by column, per non-empty header
        values = [sheet.col(i)[len(constants.MONTHHEADERS):] for i,head in zip(range(index,index+len(monthheaders)),monthheaders) if head]
        values = list(zip(*values))

        ## Transpose data from columns/fields to rows/records and convert to a dictionary with header keys
        values = [dict(list(zip(valueheaders,[cell.value for cell in value]))) for value in values]

        ## Update quantity/cost values with base item info
        itemtotals = [item.copy() for item in itemdefs]
        for item,value in zip(itemtotals,values):
            item.update(value)

        ## If the inventory length is different from the item info length, raise an exception
        if len(itemtotals) != len(itemdefs): raise ValueError("Itemtotals is not same length as itemdefs")

        ## Remove nonitems
        itemtotals = [item for item in itemtotals if item['item']]

        ## Add Month's Inventory to output
        output.append(classes.Inventory(date = date,itemtotals = itemtotals))

        ## Increment to next possible set of headers
        index += len(monthheaders)-1

    ## Return list of Inventory objects
    return output

def sortinventories(inventories, reverse = False):
    """ Sorts inventories by month/year """
    return sorted(inventories,key = lambda inv: inv.date, reverse=reverse)

def export_csv(inventory,file):
    """ Exports Inventory item dicts to a Comma-Separated Value formatted file. Overwrites if file exists. """

    with open(file,'w',newline="") as f:
        writer = csv.DictWriter(f,fieldnames = iconstants.EXPORTHEADERS)
        writer.writeheader()
        writer.writerows(inventory)

def export_db_costs(inventory,database):
    """ Exports Inventroy item dicts to the supplied InventoryDatabase. Updates the "costs" and "inventory" Tables, and adds items to the "item" table if necessary. """

    costs = set([iclasses.ItemCost(**item) for item in inventory])
    print(len(costs))
    costs = [cost.todict() for cost in costs]
    print(len(costs))

    coststable = database.tables['costs']
    errors = list()
    for cost in costs:
        try:
            coststable.insertrow(**cost)
        except Exception as e:
            errors.append(e)
    return errors

def export_db_quantities(inventory,database):
    """ Exports Inventroy item dicts to the supplied InventoryDatabase. Updates the "costs" and "inventory" Tables, and adds items to the "item" table if necessary. """

    i1,i2 = iclasses.Item(**inventory[0]),iclasses.Item(**inventory[237])
    items = [item.todict() for item in set(iclasses.Item(**item) for item in inventory)]
    costs = [iclasses.ItemCost(**item).todict() for item in inventory]
    inventories = [iclasses.InventoryItem(**item).todict() for item in inventory]

    itemstable = database.tables['items']
    indatabase = itemstable.getitembyid(*[item['itemid'] for item in items])
    missing = [item for item,indb in zip(items,indatabase) if not indb]
    for item in missing:
        itemstable.insertrow(**item)

    errors = list()
    inventorytable = database.tables['inventory']
    for item in inventories:
        try:
            inventorytable.insertrow(**item)
        except Exception as e:
            errors.append(e)
    return errors



