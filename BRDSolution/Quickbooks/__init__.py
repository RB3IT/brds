""" BRDSolution.Quickbooks

    A module for manipulation of Quickbooks data

"""

import csv
import datetime
import json
import pathlib
from alcustoms import sql

def parse_reportfile(file):
    """ Quickbooks outputs poorly-structured csv files that need further parsing.
    
        Quickbooks Layout is a Recursive Category->[Subcategories],Items
        This is translated to a nested Dict format with keys:
            Items, a list of non-recursive items;
            Categories, a dict of Subcategories with their Name as their key;
            Totals for the "Total" line.
        Items and Totals are dicts with values paired to the headerrow.
        Note that the topmost dict does not have a category name available.

        Example:
            Input-
                [Blank Column]      [... Headers]
                Category
                Subcategory
                                    [... Item Values]
                Total Subcategory   [... Subcategory Totals]
                Total Category      [... Category Totals]

            Output-
                {
                    "Items": [],
                    "Categories": {
                        "Category": {
                            "Items":[],
                            "Categories": {
                                "Subcategory": {
                                    "Items": [... Item Values],
                                    "Categories": [],
                                    "Totals": [... Subcategory Totals]
                                }
                            },
                            "Totals": [... Category Totals]
                        }
                    },
                    "Totals": []
                }
    """
    def getnewlevel():
        return dict(Items = [], Categories={}, Totals=[])

    with open(file,'r') as f:
        reader = csv.reader(f)
        headerrow = next(reader)
        if headerrow[0]:
            raise RuntimeError("Failed to parse report file")
        headerrow[0] = "__TYPE"
        output = getnewlevel()
        def recursion(currentlevel):
            ## Try to parse next row
            try: row = next(reader)
            except StopIteration: return
            while row:
                row = dict(list(zip(headerrow,row)))
                ## Category Row
                if row["__TYPE"]:
                    ## Total Line
                    if row["__TYPE"].startswith("Total"):
                        row.pop("__TYPE")
                        currentlevel['Totals'] = row
                        return
                    subcategory = getnewlevel()
                    currentlevel['Categories'][row['__TYPE']] = subcategory
                    recursion(subcategory)
                else:
                    row.pop("__TYPE")
                    currentlevel['Items'].append(row)
                try: row = next(reader)
                except StopIteration: return

        recursion(output)
    return output

def test_setup_db(dbfile):
    dbfile = pathlib.Path(dbfile).resolve()
    if dbfile.exists(): dbfile.unlink()
    with sql.Database(dbfile) as db:
        with db.cursor() as c:
            c.executescript("""
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    parent INTEGER REFERENCES categories,
    UNIQUE (category,parent) ON CONFLICT IGNORE
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category INTEGER REFERENCES categories,
    type TEXT,
    date timestamp,
    num TEXT,
    sourcename TEXT,
    memo TEXT,
    quantity REAL,
    cost REAL,
    total REAL,
    dateadded timestamp /* To enforce unique values */
);
""")

def test_update_db(file, dbfile):
    """ TEST FUNCTION """
    from alcustoms import IntegerPointer
    totalitems = IntegerPointer()
    today = datetime.datetime.today()
    def recurse(category, categoryid = None):
        for item in category['Items']:
            v = {"".join(k.lower().split()):item[k] for k in ["Type","Date","Num","Memo","Source Name"]}
            for k,Key in [ ("quantity", "Qty"), ("cost", "Cost Price"), ("total", "Amount")]:
                v[k] = item[Key]
            v['date'] = datetime.datetime.strptime(v['date'],"%m/%d/%Y")
            v['category'] = categoryid
            ## Have to check that we're not adding duplicates
            ## Unfortunately, there are no unique identifiers for lineitems
            row = ordertable.quickselect(**v).first()
            if row:
                ## Check if row was added during this run: if it wasn't
                ## then we are assuming that it's a duplicate
                if row.dateadded != today:
                    continue
                ## If it was added as part of this loop, then it's a different
                ## lineitem, even if everything else is the same
            v['dateadded'] = today
            ordertable.addrow(**v)
            totalitems.increment()
        for cat, cdict in category['Categories'].items():
            cid = categorytable.get_or_addrow(category = cat, parent = categoryid).first()
            recurse(cdict,cid)

    with open(file,'r') as f:
        data = json.load(f)
    with sql.Database(dbfile, row_factory = sql.advancedrow_factory, detect_types = sql.PARSE_DECLTYPES) as db:
        ordertable = db.getadvancedtable("orders")
        categorytable = db.getadvancedtable("categories")
        with db.cursor() as c:
            recurse(data)
        def recurseitems(category, items = 0):
            items += len(category['Items'])
            for cat in category['Categories'].values():
                items = recurseitems(cat, items)
            return items
        items = recurseitems(data)
        print("Data Total Items:",items)
        print("Items Added:",totalitems)
        print("Total Items in DB:", len(ordertable.selectall()))

def test_analyse_function(file, dbfile):
    """ TEST FUNCTION """
    with open(file,'r') as f:
        data = json.load(f)

    db = sql.Database(dbfile, row_factory= sql.advancedrow_factory, detect_types = sql.PARSE_DECLTYPES)
    try:
        items = db.getadvancedtable("orders").selectall()
    finally:
        db.close()

    items = {item.item:item for item in items}
    inventory = data['Categories']['Inventory']
    for itemcategory in inventory['Categories'].values():
        for item,subdict in itemcategory['Categories'].items():
            itemname = item.split("(")[0].strip()
            if itemname in items:
                print(itemname)
            else:
                print(">>>",itemname)

if __name__ == "__main__":
    #inputfile = "qbout.CSV"
    #output = parse_reportfile(inputfile)
    outputfile = "OUTPUT.json"
    # with open(outputfile,'w') as f:
    #   json.dump(output,f)
    dbfile = "db2.sqlite3"
    #test_setup_db(dbfile)
    test_update_db(outputfile, dbfile)
    #test_analyse_function(outputfile, dbfile)
    print("done")
