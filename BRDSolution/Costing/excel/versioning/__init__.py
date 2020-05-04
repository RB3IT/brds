""" BRDSolution.Costing.excel.versioning

    A module to handle translation between different versions of the Excel Costing Sheet.

    Each new version of the Excel Costing Sheet TEMPLATE file should be stored in this directory and be
    accompanied by a Python Script to handle it. TEMPLATE files should be named "TEMPLATE V{version}.xlsx"
    and the corresponding Script simply as "v{version}.py". "{version}" should be a valid DotVersion
    representation (from alcustoms.methods): periods (".") in the DotVersion may be substituted for
    underscores ("_") in the file names, but should be retained within the files themselves.
    
    Example:
        A minor updates to Version 1 makes more sense for the next version to be Version "1.1" instead
        of "2". The TEMPLATE_VERSION cell of this new file should contain "1.1" and a Python Script
        should be created with a VERSION Attribute of DotVersion("1.1"). The Template file can be
        named "TEMPLATE V1.1.xlsx" or "TEMPLATE V1_1.xlsx"; for the Script file, it is more secure to
        import the file using "import v1_1" and therefore it would be better to name the file "v1_1.py"
        instead of "v1.1.py".
    
    The Python Script is required to have (at minimum) the following:
    Attributes:
        VERSION: DotVersion representation of the TEMPLATE's Version
    Functions:
        (Note: for all of these methods, if the method fails due to incompatibility with the current method, this
        module's VersionError should be raised)
        parsesheet(file: "pathlib.Path", wb: "openpyxl.Workbook")-> "CostingSheet": Converts the given Workbook into a
            CostingSheet Instance
        updatesheet(costingsheet: "CostingSheet")-> "CostingSheet": Converts an older version CostingSheet to the
            given Version (replacing the current Excel file)
        parsesheet_toDoor(costingsheet: "CostingSheet")-> "NewDadsDoor.Door": Converts a CostingSheet Instance into a NewDadsDoor.Door
        writesheet_fromDoor(file: "pathlib.Path", sheet: "NewDadsDoor.Door"): Creates an Excel Costing sheet for
            the given Version based on a NewDadsDoor Door Instance

    Attribute values will be verified, but method returns will not be: it is suggested that unittests be added to
    ensure proper functionality.

    Note that the updatesheet() function for v1 (the very first Template Version) raises a VersionError as there are
    no previous version to upgrade from.

    Automatic discovery of TEMPLATES and Scripts was considered, but moving forward it's unlikely that the
    Costing Sheet Version will be updated often enough to merit it. For this reason, new version should be imported here
    and registered via register_version (this may be done at the bottome of this file).
"""
## Builtin
import inspect
## Third Party
from alcustoms.methods import DotVersion

class VersionError(AttributeError): pass

## A dict of registered Costing Sheet Versions
VERSIONS = {}

__REQUIREDATTRIBUTES = ["VERSION",]
__REQUIREDMETHODS = ['parsesheet', 'updatesheet', 'parsesheet_toDoor', 'writesheet_fromDoor']

def register_version(module):
    """ Registers a Version's module (script) for use.
    
        Modules to be registered must have the following attributes: {', '.join(__REQUIREDATTRIBUTES)}
        Modules to be registered must have the following methods: {', '.join(__REQUIREDMETHODS)}
    """
    if not inspect.ismodule(module):
        raise TypeError("module should be a Python module")
    
    if not all(hasattr(module,attr) for attr in __REQUIREDATTRIBUTES):
        raise ValueError(f"Version {module.__name__} module should have the following Attributes: {', '.join(__REQUIREDATTRIBUTES)}")

    if not all(hasattr(module,meth) and inspect.isfunction(getattr(module,meth)) for meth in __REQUIREDMETHODS):
        print([(meth,hasattr(module,meth), inspect.isfunction(getattr(module,meth,None))) for meth in __REQUIREDMETHODS])
        raise ValueError(f"Version {module.__name__} module should have the following Functions: {', '.join(__REQUIREDMETHODS)}")

    dotversion = module.VERSION
    if not isinstance(dotversion,DotVersion):
        try: dotversion = DotVersion(dotversion)
        except:
            raise TypeError(f"Version {module.__name__}'s VERSION attribute should be a valid DotVersion")
    
    if dotversion in VERSIONS:
        raise RuntimeError(f"Template Version {module.VERSION} has already been registered")

    VERSIONS[dotversion] = module



def getsheetversion(file,wb):
    """ Given a file and workbook, determine the appropriate Costing Sheet Class Version
    
        VersionErrors raised by a Version module's parsesheet method will not be caught
        as this would indicated a malformed Excel Sheet and should not be ignored.
    """
    ## Can't do anything if "TEMPLATE_VERSION" not defined
    if "TEMPLATE_VERSION" not in wb.defined_names: return None
    version = DotVersion(wb.defined_names['TEMPLATE_VERSION'])
    ## Don't have the version registered
    if version not in VERSIONS: return None
    return VERSIONS[version].parsesheet(file,wb)


from .import v1
register_version(v1)
#register_version(v2)