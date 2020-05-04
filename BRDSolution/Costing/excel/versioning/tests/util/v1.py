from NewDadsDoor.classes import Spring
from NewDadsDoor import methods

## Solutions for test_parsesheet
PARSESHEETS = [
    dict(file = "8 x 8 Costing Sheet v1.xlsx", width = 8, height = 8, totalextracost = 1_029.74, totalbasecost = 985.67),
    ]

## Solutions for test_parsesheet_toDoor
DOORS = [
    dict(file = "8 x 8 Costing Sheet v1.xlsx", door = methods.basic_torsion_door("8ft","8ft"))
    ]

DOORS[0]['door'].setpipe(pipewidth = 98.0, shell = 4, shaft = 1.25,
                 assembly = [Spring(.4375, od = 3.75, uncoiledlength = 36.75/.437),])

