import sys, os
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
sys.path.insert(0, PROJECT_DIR)

import unittest
from OOMMFTools import odtchomp
class Test_headers_prettify(unittest.TestCase):
    def test_headers_prettify(self):
        '''
        Test headers_prettify
        key of dictionary made up of evolver, givenName, quantity
        '''
        test_dict = {'key1:part1:part2': 'Zed', 'key2:part1:part2': 39, 'key3:part1:part2': 9}

        test_output = odtchomp.headers_prettify(test_dict)
        print(test_output)
        self.assertEqual(test_output, {'key1 part1 part2': 'Zed', 'key2 part1 part2': 39, 'key3 part1 part2': 9})

    def test_headers_prettify_key_collision(self):
        '''
        There is something there about key collisions.
        At the moment all it does is log the fact that a 'key collision' has
        happened.
        '''
        pass

class Test_list_prettify(unittest.TestCase):
    def test_list_prettify(self):
        '''
        Test headers_prettify
        key of dictionary made up of evolver, givenName, quantity
        '''
        test_list = ['key1:part1:part2', 'key2:part1:part2', 'key3:part1:part2']

        test_output = odtchomp.list_prettify(test_list)
        print(test_output)
        self.assertEqual(test_output, ['key1 part1 part2', 'key2 part1 part2', 'key3 part1 part2'])



class Test_namepolish(unittest.TestCase):
    '''
    Probably need around 10 tests for the different if options.
    '''
    def test1_namepolish_givenName_quantity(self):
        '''
        Name polish is called by headers_prettify.
        '''
        name = 'evolver:givenName:quantity'
        # 
        uniquenessCheck = [['evolver2', 'givenName', 'quantity'], ['evolver2', 'givenName2', 'quantity']]
        new_name = odtchomp.namepolish(name, uniquenessCheck)
        self.assertEqual(new_name, 'givenName quantity')

    def test2_namepolish_evolver_givenName_quantity(self):
        '''
        Name polish is called by headers_prettify.
        '''
        name = 'evolver:givenName:quantity'
        # no unique elements, so take full thing to describe
        uniquenessCheck = [['evolver', 'givenName', 'quantity'], ['evolver', 'givenName', 'quantity']]
        new_name = odtchomp.namepolish(name, uniquenessCheck)
        self.assertEqual(new_name, 'evolver givenName quantity')

    def test3_namepolish_quantity(self):
        '''
        Name polish is called by headers_prettify.
        '''
        name = 'evolver:givenName:quantity'
        # 'quantity' is unique, so doesn't need any more descriptors
        uniquenessCheck = [['evolver', 'givenName', 'quantity'], ['evolver2', 'givenName2', 'quantity2']]
        new_name = odtchomp.namepolish(name, uniquenessCheck)
        self.assertEqual(new_name, 'quantity')

    def test4_namepolish_evolver_givenName_quantity2(self):
        '''
        Name polish is called by headers_prettify.
        '''
        name = 'evolver:givenName:quantity'
        # evolvers are 
        uniquenessCheck = [['evolver', 'givenName', 'quantity'], ['evolver2', 'givenName', 'quantity']]
        new_name = odtchomp.namepolish(name, uniquenessCheck)
        self.assertEqual(new_name, 'evolver givenName quantity')

    def test5_namepolish_givenName_evolver_quantity_protectEvolver(self):
        '''
        Name polish is called by headers_prettify.
        '''
        odtchomp.PROTECTED_NAMES = ["evolver_prot"]
        name = 'evolver_prot:givenName:quantity'
        uniquenessCheck = [['evolver_prot', 'givenName', 'quantity'], ['evolver2', 'givenName', 'quantity']]
        new_name = odtchomp.namepolish(name, uniquenessCheck)
        self.assertEqual(new_name, 'givenName evolver quantity')


class Test_filterOnPos(unittest.TestCase):
    '''
    Returns list if a string is found in a particular position in that list.
    '''
    def test_filterOnPos_item_in_two_sublists(self):
        '''
        '''
        inList = [['item1', 'item2', 'item3'], ['item1', 'item5', 'item6']]
        item = 'item1'
        dex = 0
        ret = odtchomp._filterOnPos(inList, item, dex)
        self.assertEqual(ret, [['item1', 'item2', 'item3'], ['item1', 'item5', 'item6']])
        
    def test_filterOnPos_item_in_one_of_two_sublists(self):
        '''
        '''
        inList = [['item1', 'item2', 'item3'], ['item4', 'item5', 'item6']]
        item = 'item1'
        dex = 0
        ret = odtchomp._filterOnPos(inList, item, dex)
        self.assertEqual(ret, [['item1', 'item2', 'item3']])
        
    def test_filterOnPos_item_in_wrong_position(self):
        '''
        '''
        inList = [['item1', 'item2', 'item3'], ['item4', 'item5', 'item6']]
        item = 'item1'
        dex = 1
        ret = odtchomp._filterOnPos(inList, item, dex)
        self.assertEqual(ret, [])

    def test_filterOnPos_empty_lists(self):
        '''
        Needs to fail nicely when given empty lists
        '''
        pass