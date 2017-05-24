import sys, os
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
sys.path.insert(0, PROJECT_DIR)

import unittest
from OOMMFTools import odtchomp
class Test_odtchomp(unittest.TestCase):
    def test_headers_prettify(self):
        '''
        Test headers_prettify
        '''
        test_dict = {'key1:part1:part2': 'Zed', 'key2:part1:part2': 39, 'key3:part1:part2': 9}

        test_output = odtchomp.headers_prettify(test_dict)
        print(test_output)
        self.assertEqual(test_output, {'key1 part1 part2': 'Zed', 'key2 part1 part2': 39, 'key3 part1 part2': 9})
        