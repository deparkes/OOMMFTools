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

class Test_replaceConfigLines(unittest.TestCase):
    def test_basic_operation(self):
        oldConfigLines = ['line1', '\n', 'line2']
        newMax = 10
        percentMagnitude = 90
        checkVectors = True
        newConfig = oommfconvert.replaceConfigLines(oldConfigLines,
                                                   newMax,
                                                   percentMagnitude,
                                                   checkVectors)
        self.assertEqual(newConfig, oldConfigLines)

    def test_misc_datascale(self):
        oldConfigLines = ['misc,datascale 10\n', '\n', 'line2\n']
        newMax = 10
        percentMagnitude = 90
        checkVectors = True
        newConfig = oommfconvert.replaceConfigLines(oldConfigLines,
                                                   newMax,
                                                   percentMagnitude,
                                                   checkVectors)
        expectedNewline = '    misc,datascale 10\n'
        self.assertEqual(newConfig, [expectedNewline,  '\n', 'line2\n'])

    def test_misc_datascale_check_vectors_false(self):
        oldConfigLines = ['misc,datascale 10\n', '\n', 'line2\n']
        newMax = 10
        percentMagnitude = 90
        checkVectors = False
        newConfig = oommfconvert.replaceConfigLines(oldConfigLines,
                                                   newMax,
                                                   percentMagnitude,
                                                   checkVectors)
        expectedNewline = 'misc,datascale 10\n'
        self.assertEqual(newConfig, [expectedNewline,  '\n', 'line2\n'])


    def test_misc_datascale_clobber_zoom(self):
        oldConfigLines = ['misc,zoom 10\n', '\n', 'line2\n']
        newMax = 10
        percentMagnitude = 90
        checkVectors = False
        newConfig = oommfconvert.replaceConfigLines(oldConfigLines,
                                                   newMax,
                                                   percentMagnitude,
                                                   checkVectors)
        expectedNewline = "    misc,zoom 0\n"
        self.assertEqual(newConfig, [expectedNewline,  '\n', 'line2\n'])


    def test_misc_datascale_misc_height(self):
        oldConfigLines = ['misc,height 20\n', '\n', 'line2\n']
        newMax = 10
        percentMagnitude = 90
        checkVectors = False
        newConfig = oommfconvert.replaceConfigLines(oldConfigLines,
                                                   newMax,
                                                   percentMagnitude,
                                                   checkVectors)
        expectedNewline = "    misc,height 18.0\n"
        self.assertEqual(newConfig, [expectedNewline,  '\n', 'line2\n'])

    def test_misc_datascale_misc_width(self):
        oldConfigLines = ['misc,width 80\n', '\n', 'line2\n']
        newMax = 10
        percentMagnitude = 90
        checkVectors = False
        newConfig = oommfconvert.replaceConfigLines(oldConfigLines,
                                                   newMax,
                                                   percentMagnitude,
                                                   checkVectors)
        expectedNewline = "    misc,width 72.0\n"
        self.assertEqual(newConfig, [expectedNewline,  '\n', 'line2\n'])

    def test_misc_datascale_with_comment(self):
        oldConfigLines = ['#with comment\n', 'misc,width 80\n', '\n', 'line2\n']
        newMax = 10
        percentMagnitude = 90
        checkVectors = False
        newConfig = oommfconvert.replaceConfigLines(oldConfigLines,
                                                   newMax,
                                                   percentMagnitude,
                                                   checkVectors)
        expectedNewline = "    misc,width 72.0\n"
        self.assertEqual(newConfig, ['#with comment\n', expectedNewline,  '\n', 'line2\n'])

    def test_misc_datascale_with_braces(self):
        oldConfigLines = ['{\n', 'misc,width 80\n', '\n', '}', 'line2\n']
        newMax = 10
        percentMagnitude = 90
        checkVectors = False
        newConfig = oommfconvert.replaceConfigLines(oldConfigLines,
                                                   newMax,
                                                   percentMagnitude,
                                                   checkVectors)
        expectedNewline = "    misc,width 72.0\n"
        self.assertEqual(newConfig, ['{\n', expectedNewline,  '\n', '}', 'line2\n'])
