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


class Test_oommfdecode_text(unittest.TestCase):
    def setUp(self):
        self.test_files_folder = 'testfiles'
        self.vector_file_text = os.path.join(TEST_DIR, 
                                        self.test_files_folder,
                                        'dw_edgefield_cut_cell4_160.ohf')
        self.headers_test = {'ystepsize': 4e-09, 'xnodes': 1250.0, 'valuemultiplier': 258967.81743932367, 'xbase': 2e-09, 'zstepsize': 8e-09, 'znodes': 1.0, 'zbase': 4e-09, 'ynodes': 40.0, 'ybase': 2e-09, 'xstepsize': 4e-09}
        self.extraCaptures_test =  {'MIFSource': 'C:/programs/oommf_old/simus/DW-150-8-transverse/DW_edgefield/dw_edgefield.mif', 'Iteration': 0.0, 'SimTime': 0.0, 'Stage': 0.0}
        self.vector_file_binary = os.path.join(TEST_DIR, 
                                        self.test_files_folder,
                                        'h2h_leftedge_40x4.ohf')

        self.targetarray_pickle = os.path.join(TEST_DIR, 
                                        self.test_files_folder,
                                        'targetarray_text.npy')
    def test_unpackFile_text_targetarray(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_text)
        #np.save(self.targetarray_pickle, targetarray)
        self.assertEqual(targetarray.all(), np.load(self.targetarray_pickle).all())
        
    def test_unpackFile_text_headers(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_text)
        self.assertEqual(headers, self.headers_test)
        
    def test_unpackFile_text_extracaptures(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_text)
        self.assertEqual(extraCaptures, self.extraCaptures_test)

class Test_oommfdecode_binary(unittest.TestCase):
    def setUp(self):
        self.test_files_folder = 'testfiles'
        self.vector_file_text = os.path.join(TEST_DIR, 
                                        self.test_files_folder,
                                        'dw_edgefield_cut_cell4_160.ohf')
        self.vector_file_binary = os.path.join(TEST_DIR, 
                                        self.test_files_folder,
                                        'h2h_leftedge_40x4.ohf')        
    def test_unpackFile_binary_targetarray(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_binary)
        self.assertEqual(targetarray, '1')
        
    def test_unpackFile_binary_headers(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_binary)
        self.assertEqual(headers, '1')
        
    def test_unpackFile_binary_extraCaptures(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_binary)
        self.assertEqual(extraCaptures, '1')
        
        
        
        
        
