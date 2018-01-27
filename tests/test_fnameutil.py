import sys, os
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
sys.path.insert(0, PROJECT_DIR)

import unittest
from oommftools import fnameutil
class Test_fnameutil(unittest.TestCase):
    def test_filterOnExtensions(self):
        '''
        Test filteronExtensions functionality.
        '''
        test_output = fnameutil.filterOnExtensions(["ohf", "omf"],["test_omf.omf", "test_ohf.ohf", "test_txt.txt"])
        print(test_output)
        self.assertEqual(test_output, ["test_omf.omf", "test_ohf.ohf"])