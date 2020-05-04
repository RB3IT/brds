## Builtin
import pathlib
import re
## 3rd Party
import openpyxl
from alcustoms.excel.Ranges import get_named_cell
from alcustoms import filemodules
from alcustoms.methods import DotVersion


## File Name pattern for Costing Sheets
COSTINGSHEETRE = re.compile("(?P<width>\d+)\s*x\s*(?P<height>\d+)\s*costing\s*sheet",re.IGNORECASE)

class CostingSheet():
    """ Represents an Excel Costing Sheet """
    def __init__(self, file: "pathlib.Path", workbook: "openpyxl.Workbook"):
        """ Initialize a new CostingSheet.

            file should be a Concrete pathlib.Path
            workbook should be an openpyxl.Workbook
        """
        self.file = file
        self.workbook = workbook

    def get_named_value(self, value):
        """ Helper function to call get_named_cell """
        try:
            cell = get_named_cell(self.workbook,value)
            return cell.value
        except: return

    @property
    def version(self):
        return DotVersion(self.get_named_value('TEMPLATE_VERSION'))

    @property
    def width(self):
        return self.get_named_value("Width")
    @property
    def height(self):
        return self.get_named_value("Height")

    @property
    def totalextracost(self):
        return self.get_named_value('TotalExtraCost')
    @property
    def totalbasecost(self):
        return self.get_named_value('TotalBaseCost')

    def __repr__(self):
        return f"{self.__class__.__name__}({self.file})"

def gathercostingsheets(dire: pathlib.Path):
    """ Returns all Excel Costing Sheets in the directory
    
        dire should be a pathlib.Path instance for an existing directory.
    """
    costingsheets, failures = [], []
    ## Get all files in the directory that match the Costing Sheet regex
    for file in filemodules.iterdir_re(dire, COSTINGSHEETRE):
        try:
            wb = openpyxl.load_workbook(file, data_only = True)
            ## Try to determine Costing Sheet Version
            sheet = versioning.getsheetversion(file,wb)
            ##  If versioning returned None, it failed
            ## (otherwise it returns an Object, which will resolve as True)
            assert sheet

        ## Couldn't open the Excel Sheet or
        ## Couldn't determine Costing Sheet Version
        except:
            failures.append(file)
        ## Successfully generated Costing Sheet
        else:
            costingsheets.append(sheet)

    return costingsheets, failures

## This module (circular import)
from . import versioning