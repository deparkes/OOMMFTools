import sys, os
import StringIO
import tempfile
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
sys.path.insert(0, PROJECT_DIR)

import unittest
from oommftools import oommfdecode
class Test_OOMMFDecode(unittest.TestCase):
    def test_groupUnpack(self):
        pass
    
    def test_unpackFile(self):
        pass
        
    def test_textDecode(self):
        pass
        
    def test_binaryDecode(self):
        pass
        
    def test_pickleArray(self):
        pass
    
    def test_matlabifyArray(self):
        pass
        
    def test_slowlyPainfullyMaximize(self):
        pass