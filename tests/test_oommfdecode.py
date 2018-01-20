import sys, os
import StringIO
import tempfile
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
sys.path.insert(0, PROJECT_DIR)

import unittest
from OOMMFTools import oommfdecode
import wx
class Test_OOMMFSelectiveTarget(unittest.TestCase):
    def setUp(self):
        app = wx.App(redirect=True, filename="oommfdecode.log")
        self.main = oommfdecode.MainFrame()
#       
#    
#    def test_OnDropFilesGoodFiles(self):
#        x = 1
#        y = 1
#        self.main.doNumpy.SetValue(True)
#        filenames = ['test.omf','test.ohf']
#        self.assertTrue(self.main.dt.OnDropFiles(x,y,filenames))
#
#    def test_OnDropFilesBadFile(self):
#        x = 1
#        y = 1
#        filenames = ['test.ozf','test.ohf']
#        self.main.doNumpy.SetValue(True)
#        self.assertEqual(self.main.dt.OnDropFiles(x,y,filenames), None)
#        
#
#    def test_groupUnpack(self):
#        pass
#        
#    def test_unpackFile(self):
#        pass
#        
#    def test_textDecode(self):
#        pass
#        
#    def test_binaryDecode(self):
#        pass
#        
#    def test_pickleArray(self):
#        pass
#        
#    def test_matlabifyArray(self):
#        pass
#    
#    def test_slowlyPainfullyMaximize(self):
#        pass
