## Test Target
from BRDSolution.Costing.excel.versioning import v1
## Test Framework
import unittest
## This Module
from BRDSolution.Costing.excel.versioning import tests as utilities, VersionError
from BRDSolution.Costing.excel.versioning.tests.util import v1 as v1_utils
from BRDSolution.Costing import excel
from NewDadsDoor.tests import methods as NDDTestMethods

COSTINGSHEETS = {}
for (file,workbook) in utilities.COSTINGSHEETS:
    try: sheet = v1.parsesheet(file,workbook)
    except VersionError: continue
    COSTINGSHEETS[sheet.file.name] = sheet

class BaseTest(unittest.TestCase):
    def test_sheets(self):
        """ Make sure we convert the expected number to CostingSheets """ 
        self.assertEqual(len(COSTINGSHEETS),1)
        self.assertTrue(all(isinstance(sheet,excel.CostingSheet) for sheet in COSTINGSHEETS.values()))
        self.assertTrue(all(sheet.version == v1.VERSION for sheet in COSTINGSHEETS.values()))

    def test_parsesheet(self):
        """ Tests the results of the parsesheet function """
        ## NOTE: Checking that it's a CostingSheet and that its version 
        ## is correct is handled in test_sheets
        EXPECTED = v1_utils.PARSESHEETS
        for test in EXPECTED:
            with self.subTest(test = test):
                sheet = COSTINGSHEETS[test['file']]
                self.assertEqual(sheet.width, test['width'])
                self.assertEqual(sheet.height, test['height'])
                self.assertAlmostEqual(sheet.totalextracost, test['totalextracost'],2)
                self.assertAlmostEqual(sheet.totalbasecost, test['totalbasecost'],2)

    def test_updatesheet(self):
        """ Tests that updatesheet raises a VersionError as v1 does not have a previous version """
        self.assertRaises(VersionError, v1.updatesheet, list(COSTINGSHEETS.values())[0])

    def test_parsesheet_toDoor(self):
        """ Tests that parsesheet_toDoor functions appropriately """
        EXPECTED = v1_utils.DOORS

        for test in EXPECTED:
            result = v1.parsesheet_toDoor(COSTINGSHEETS[test['file']])
            try:
                self.assertEqual(result,test['door'])
            except Exception as e:
                print(NDDTestMethods.format_comparison(NDDTestMethods.compare_door(result, test['door'])))
                raise e

