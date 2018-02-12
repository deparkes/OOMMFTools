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
import io
from oommftools.fnameutil import filterOnExtensions
import scipy.io as spio
import cPickle as pickle
import struct

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
        np.testing.assert_array_equal(targetarray, np.load(self.targetarray_pickle))
        
    def test_unpackFile_text_headers(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_text)
        self.assertEqual(headers, self.headers_test)

    def test_unpackFile_headers_keys(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_text)
        self.assertEqual(headers.keys().sort(), self.headers_test.keys().sort())
        
    def test_unpackFile_text_extracaptures(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_text)
        self.assertEqual(extraCaptures, self.extraCaptures_test)

class Test_oommfdecode_binary(unittest.TestCase):
    def setUp(self):
        self.test_files_folder = 'testfiles'
        self.vector_file_binary = os.path.join(TEST_DIR, 
                                        self.test_files_folder,
                                        'h2h_leftedge_40x4.ohf')
        self.headers_test = {'ystepsize': 1e-08, 'xnodes': 160.0, 'valuemultiplier': 1.0, 'xbase': 5e-09, 'zstepsize': 1e-08, 'znodes': 4.0, 'zbase': 5e-09, 'ynodes': 40.0, 'ybase': 5e-09, 'xstepsize': 1e-08}
        
        self.extraCaptures_test =  {'MIFSource': '/local/home/donahue/oommf/app/oxs/examples/h2h_edgefield.mif', 'Iteration': 0.0, 'SimTime': 0.0, 'Stage': 0.0}
                                        
        self.targetarray_pickle = os.path.join(TEST_DIR, 
                                        self.test_files_folder,
                                        'targetarray_binary.npy')                                        
    def test_unpackFile_binary_targetarray(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_binary)
        #np.save(self.targetarray_pickle, targetarray)
        np.testing.assert_array_equal(targetarray, np.load(self.targetarray_pickle))
        
    def test_unpackFile_binary_headers(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_binary)
        self.assertEqual(headers, self.headers_test)
        
    def test_unpackFile_binary_extraCaptures(self):
        (targetarray, headers, extraCaptures) = oommfdecode.unpackFile(self.vector_file_binary)
        self.assertEqual(extraCaptures, self.extraCaptures_test)
        
        
class Test_pickleArray(unittest.TestCase):
    def setUp(self):
        self.array = np.array([1., 2., 3.])
        self.headers = {'Name': 'Headers', 'Value': 1}
        self.extraCaptures = {'Capture1': 1, 'Capture2': 'two'}
        self.filename = os.path.join(tempfile.gettempdir(),
                                        'test.npy')
        
    def test_pickle_array(self):
        oommfdecode.pickleArray(self.array, self.headers, self.extraCaptures, self.filename)
        with open(self.filename, "r") as input_file:
            e = pickle.load(input_file)
        self.assertEqual(e[0].all(), np.array([1., 2., 3.]).all())
        self.assertEqual(e[1], dict(self.headers.items() + self.extraCaptures.items()))
 
class Test_matlabifyArray(unittest.TestCase):
    def setUp(self):
        self.array = np.array([1., 2., 3.])
        self.headers = {'xstepsize': 1, 'ystepsize': 2, 'zstepsize': 3}
        self.extraCaptures = {'Capture1': 1, 'Capture2': 'two'}
        self.filename = os.path.join(tempfile.gettempdir(),
                                        'test.mat')
        
    def test_matlabify_array(self):
        oommfdecode.matlabifyArray(self.array, self.headers, self.extraCaptures, self.filename)
        e = spio.loadmat(self.filename)
        self.assertEqual(e['OOMMFData'].all(), np.array([[1., 2., 3.]]).all())
        self.assertEqual(e['Capture2'], np.array([u'two']))
        self.assertEqual(e['Capture1'], np.array([[1]]))
        self.assertEqual(e['GridSize'].all(), np.array([[1., 2., 3.]]).all())
        
class Test_textDecode(unittest.TestCase):
    def setUp(self):
        to_write = '-0.80  0.52  0.00\n-0.35  0.27  0.00\n-0.21  0.17  0.00'
        self.output = StringIO.StringIO(to_write)
        self.outArray = np.zeros((3, 3, 3, 3))
        self.headers = {'xnodes': 1.0, 'znodes': 1.0, 'ynodes'                   : 3.0, 'valuemultiplier': 2}
        self.extraCaptures = {'a': 1, 'b': 2, 'c': 3}
        self.test_array = np.array([[[[-1.6 ,  1.04,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[-0.7 ,  0.54,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[-0.42,  0.34,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]]],


                                   [[[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]]],


                                   [[[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]],

                                    [[ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ],
                                     [ 0.  ,  0.  ,  0.  ]]]])
    def test_textDecode(self):
        (targetarray, headers, extraCaptures) = oommfdecode._textDecode(self.output, self.outArray, self.headers, self.extraCaptures)
        #self.assertEqual(targetarray.all(), np.array(1))
        np.testing.assert_array_equal(targetarray, self.test_array)

class Test_binaryDecode(unittest.TestCase):
    def setUp(self):
        self.outArray = np.zeros((3, 3, 3, 3))
        self.headers = {'xnodes': 1.0,
                        'znodes': 1.0,    
                        'ynodes' : 3.0, 
                        'valuemultiplier': 1}
        self.extraCaptures = {'a': 1, 'b': 2, 'c': 3}
        self.chunksize_4 = 4
        self.chunksize_8 = 8
        self.test_array = np.array([[[[-1.6 ,  1.04,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ]],

                                [[-0.7 ,  0.54,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ]],

                                [[-0.42,  0.34,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ]]],


                               [[[ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ]],

                                [[ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ]],

                                [[ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ]]],


                               [[[ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ]],

                                [[ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ]],

                                [[ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ],
                                 [ 0.  ,  0.  ,  0.  ]]]])
        self.output_little = io.BytesIO(struct.pack('<%sf' % self.test_array.size, *self.test_array.flatten('F')))
        self.output_big = io.BytesIO(struct.pack('>%sf' % self.test_array.size, *self.test_array.flatten('F')))            
    def test_binaryDecode_little_4(self):
        (targetarray, headers, extraCaptures) = oommfdecode._binaryDecode(self.output_little, 
                                  self.chunksize_4, 
                                  struct.Struct("<f"), 
                                  self.outArray, 
                                  self.headers, 
                                  self.extraCaptures)
        np.testing.assert_array_equal(targetarray,self.test_array)

    def test_binaryDecode_big_4(self):
        (targetarray, headers, extraCaptures) = oommfdecode._binaryDecode(self.output_big, 
                                  self.chunksize_4, 
                                  struct.Struct(">f"), 
                                  self.outArray, 
                                  self.headers, 
                                  self.extraCaptures)
        np.testing.assert_array_equal(targetarray,self.test_array)

    def test_binaryDecode_big_8(self):

        self.test_files_folder = 'testfiles'
        filename = os.path.join(TEST_DIR, 
                                        self.test_files_folder,
                                        'h2h_leftedge_40x4_test.ohf')
        headers = {'xnodes': 2, 'ynodes': 2, 'znodes': 2}
        with open(filename, 'rb') as f:
            (targetarray, headers, extraCaptures) = oommfdecode._binaryDecode(f, 
                          self.chunksize_8, 
                          struct.Struct(">d"), 
                          self.outArray, 
                          headers, 
                          self.extraCaptures)
            #print(struct.Struct(">d").unpack(f.read(8)))

        np.testing.assert_array_equal(targetarray,self.test_array)
