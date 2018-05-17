from future import standard_library
standard_library.install_aliases()
import sys, os
import io
import tempfile
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
sys.path.insert(0, PROJECT_DIR)

import unittest
from oommftools.core import oommfconvert as oommfconvert


class Test_getOOMMFPath(unittest.TestCase):
    def setUp(self):
        with tempfile.NamedTemporaryFile(delete=False) as self.valid_file:
            # Create dummy oommf.path file
            self.valid_file.write(r'C:\oommf-1.2a5bis\oommf.tcl'.encode())
            self.valid_file.flush()

        with tempfile.NamedTemporaryFile(delete=False) as self.invalid_path:
            # Create dummy oommf.path file
            self.invalid_path.write(r'C:\oommf-1.2a5bis'.encode())
            self.invalid_path.flush()

    def test_valid_path(self):
        path = oommfconvert.getOOMMFPath(self.valid_file.name)
        self.assertEqual(path, r'C:\oommf-1.2a5bis\oommf.tcl')

    def test_invalid_path(self):
        path = oommfconvert.getOOMMFPath(self.invalid_path.name)
        self.assertEqual(path, None)

    def test_no_file_found(self):
        path = oommfconvert.getOOMMFPath('bad/path')
        self.assertEqual(path, None)


class Test_OOMMFConvert(unittest.TestCase):
    def test_doImages(self):
        pass
    def test_resolveConfiguration(self):
        pass
    def test_spliceConfig(self):
        pass
    def test_doMovies(self):
        pass
