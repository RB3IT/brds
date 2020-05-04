""" BRDSolution.Costing.excel.versioning.v1

    Companion Script for Version 1 Costing Sheets

    Notes on Version 1:
        Doors are all Costed as BRD Flat Slat with no Weatherseal.
        Extras:
            Washers for Cast Endlocks (but not the Cast Endlock upcharge)
            Sprocket and Roller Chain for Duplex Setup (No Steel Plate)
        Manually Set Values:
            Height, Width
            Slat Type, Length, and Count (even though all Costing Sheets are BRD)
            Bottom Bar Feeder slat Type
            Bottom Bar Bolt Count
            Hood Type, Unit Length, and Labor
            Casting Types and Quantities
            Spring Type, unit Length, and Quantity
            Additional Springs require new lines
            Shaft Type and Quantity
            Washer Bearing Type
            Shaft Type and Unit Length
            Plugend Washer and Shaft Type
            Tube Type
            Barrel Ring Type and Quantity
            Tube Bearing Type
        Calculated Values:
            Bottom Bar Angle, Rubber, and Slat Unit Length
            Bottom Bar Nut Quantity
            Cast Endlock Washers, Stamped Endlocks, and Rivet Quantity
            Endplate Bolts, Washer, and Nuts Quantities
            Tracks Bolts and Nuts Quantities
            Hood Rivets Quantity
            Pipe Unit Size
            Inner, Outer, and Wall Track Unit Size

"""
from BRDSolution.Costing.excel import CostingSheet
from BRDSolution.Costing.excel.versioning import VersionError
from BRDSolution.inventory import constants
from NewDadsDoor import classes, methods as nddmethods, constants as nddconstants
from alcustoms.excel.Tables import get_table_by_name
from alcustoms.measurement import Imperial

VERSION = "1"

def fixwire(wiresize):
    """ There is precision discrepency between NDD and the Inventory
        naming which raises an error because NDD doesn't want to make assumptions """
    wiresize = float(wiresize)
    ## Some wires have their 
    if wiresize == .437:
        return .4375
    return wiresize

def parsesheet(file: "pathlib.Path", wb: "alcustoms.excel.Workbook") -> "CostingSheet":
    """ Converts the given Workbook into a CostingSheet Instance """
    sheet = CostingSheet(file, wb)
    if not sheet.version == VERSION: raise VersionError("Invalid Version")
    return sheet

def updatesheet(costingsheet: "CostingSheet")-> "CostingSheet":
    """ Converts an older version CostingSheet to the given Version (replacing the current Excel file)
    
        v1 is the first version, and therefore this method always raises a VersionError as there are
        no valid versions to upgrade from.
    """
    raise VersionError("Cannot upgrade to Template Version 1: no valid previous Versions")

def parsesheet_toDoor(costingsheet: "CostingSheet")->"NewDadsDoor.Door":
    """ Converts a CostingSheet Instance into a NewDadsDoor.Door """
    ## Convert feet to inches (or otherwise could convert to a string)
    door = nddmethods.basic_torsion_door(costingsheet.width*12, costingsheet.height*12)
    table = get_table_by_name(costingsheet.workbook, "CostsTable")
    ## First item is header list
    _,*rows = table.todicts()

    springs = filter(lambda row: constants.SPRINGRE.match(row['Item']),rows)
    springs = [(constants.SPRINGRE.search(row['Item']),row['Unit/Qty']*12) for row in springs]
    wires = [classes.Spring(wire = fixwire(spring['wire']), od = float(spring['size']),
                            coiledlength = float(length)) for spring,length in springs]
    castings = _convert_castings(filter(lambda row: constants.CASTINGRE.match(row['Item']), rows))
    sockets = nddmethods.build_sockets(wires, castings)
    door.pipe.assembly = sockets

    shaft = list(filter(lambda row: row['Subcomponent'] == "Assembly" and "Solid Shaft" in row['Item'], rows))
    if shaft:
        shaft = shaft[0]
        shaftsize = constants.SHAFTRE.match(shaft['Item']).group("shaftsize")
        shaftsize = Imperial(shaftsize)



    slats = list(filter(lambda row: row['Subcomponent'] == "Curtain" and "Slats" in row['Item'], rows))
    if slats:
        slats = slats[0]
        curtainslats = door.curtain.slatsections()[0]
        if "528" in slats['Item ID']: curtainslats.slat = "2 1/2 INCH FLAT SLAT"
        else: curtainslats.slat = "2 7/8 INCH CROWN SLAT"
        curtainslats.slats = slats['Qty']

    return door

def _convert_castings(castings):
    """ Converts a list of castings into CastingSets """
    output = []
    for row in castings:
        ## Casting is not be used, so skip it
        if not row['Qty']: continue
        research = constants.CASTINGRE.search(row['Item'])
        size = research['size']
        if research['subtype'] == "4S2":
            size = 2
        lookupname = f"Standard {research['size']} {research['type'].capitalize()}"
        casting = nddconstants.CASTINGLOOKUP[lookupname]
        casting['bore'] = research['bore']
        for qty in range(row['Qty']):
            output.append(casting)
    return output


def writesheet_fromDoor(file: "pathlib.Path", sheet: "NewDadsDoor.Door"):
    """ Creates an Excel Costing sheet for the given Version based on a NewDadsDoor Door Instance """

def determine_pipe(costingsheet: "CostingSheet")->"NewDadsDoor.Pipe":
    """ Parses the CostingSheet to determine the Pipe specifications and returns a
        NewDadsDoor.Pipe instance (with complete Assembly)"""


