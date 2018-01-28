import sys, os
import StringIO
import tempfile
import numpy as np
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
sys.path.insert(0, PROJECT_DIR)

import unittest
from oommftools import oommfdecode


import StringIO
from oommftools.fnameutil import filterOnExtensions


class Test_oommfdecode(unittest.TestCase):
    def setUp(self):
        self.test_files_folder = 'testfiles'
        self.vector_file_text = os.path.join(TEST_DIR, 
                                        self.test_files_folder,
                                        'sliding_field0.ovf')
        print(self.vector_file_text)
        self.vector_file_binary = os.path.join(TEST_DIR, 
                                        self.test_files_folder,
                                        'h2h_leftedge_40x4.ohf')

    def test_unpackFile_text(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_text)
        assertEqual(targetarray, '1')
        
    def test_unpackFile_binary(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_binary)
        self.assertEqual(targetarray, '1')
        
        
        
        
        
