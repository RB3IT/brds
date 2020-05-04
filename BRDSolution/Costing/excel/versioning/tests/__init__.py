## Test Target
from BRDSolution.Costing.excel import versioning
## Test Framework
import unittest
## This Module
from BRDSolution.Costing.excel import COSTINGSHEETRE
## Builtin
import pathlib
## Third party
import openpyxl

COSTINGSHEETS = [(file,openpyxl.load_workbook(file, data_only= True)) for file in (pathlib.Path(__file__).parent / "testsheets").resolve().iterdir() if file.is_file() and COSTINGSHEETRE.search(file.name)]

if __name__ == "__main__":
    path = pathlib.Path.cwd()
    tests = unittest.TestLoader().discover(path)
    unittest.TextTestRunner().run(tests)