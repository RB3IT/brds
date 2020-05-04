## Builtin
import csv
import traceback
## This Module
from BRDSolution.inventory import constants

def exportitemstocsv(file,items):
    with open(file,'w',newline="") as f:
        writer = csv.writer(f)
        for item in items:
            if item.databaseid and item.date:
                writer.writerow([item.databaseid,item.date.strftime(constants.DATEFORMAT),item.vendor,item.cost])


def exportitemstodb(table,items):
    failures = []
    for item in items:
        if item.databaseid and item.date:
            try:
                table.insertrow(itemid = item.databaseid, date = item.date.strftime(constants.DATEFORMAT), vendor = item.vendor, cost = item.cost)
            except:
                failures.append(f"{item.databaseid},{item.date.strftime(constants.DATEFORMAT)}\n{traceback.format_exc()}")