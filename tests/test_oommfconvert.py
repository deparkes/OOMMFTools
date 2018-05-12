from future import standard_library
standard_library.install_aliases()
import sys, os
import io
import tempfile
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
sys.path.insert(0, PROJECT_DIR)

import unittest
from oommftools import oommfconvert
class Test_OOMMFConvert(unittest.TestCase):
    def test_doImages(self):
        pass
    def test_resolveConfiguration(self):
        pass
    def test_spliceConfig(self):
        pass
    def test_doMovies(self):
        pass
