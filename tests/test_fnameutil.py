import sys, os
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
sys.path.insert(0, PROJECT_DIR)

from OOMMFTools import fnameutil

def test_filterOnExtensions():
    test = fnameutil.filterOnExtensions(["one, two, three"],["four, five, six"])
    assert test == 5