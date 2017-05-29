import sys, os
import StringIO
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
    
    '''
    def test1_quantity(self):
        '''
        Name polish is called by headers_prettify.
        '''
        name = 'evolver:givenName:quantity'
        uniquenessCheck = [['evolver', 'givenName', 'quantity'], ['evolver', 'givenName', 'quantity2']]
        new_name = odtchomp.namepolish(name, uniquenessCheck)
        self.assertEqual(new_name, 'quantity')

    def test2_givenName_quantity(self):
        '''
        Name polish is called by headers_prettify.
        '''
        name = 'evolver:givenName:quantity'
        uniquenessCheck = [['evolver', 'givenName', 'quantity'], ['evolver', 'givenName2', 'quantity']]
        new_name = odtchomp.namepolish(name, uniquenessCheck)
        self.assertEqual(new_name, 'givenName quantity')

    def test3_evolver_givenName_quantity(self):
        '''
        Name polish is called by headers_prettify.
        '''
        name = 'evolver:givenName:quantity'
        uniquenessCheck = [['evolver', 'givenName', 'quantity'], ['evolver2', 'givenName', 'quantity']]
        new_name = odtchomp.namepolish(name, uniquenessCheck)
        self.assertEqual(new_name, 'evolver givenName quantity')

    def test4_givenName_evolver_quantity(self):
        '''
        Name polish is called by headers_prettify.
        '''
        odtchomp.PROTECTED_NAMES = ["evolver_prot"]
        name = 'evolver_prot:givenName:quantity'
        uniquenessCheck = [['evolver_prot', 'givenName', 'quantity'], ['evolver2', 'givenName', 'quantity']]
        new_name = odtchomp.namepolish(name, uniquenessCheck)
        self.assertEqual(new_name, 'givenName evolver_prot quantity')

    def test5_givenName_evolver_quantity(self):
        '''
        Name polish is called by headers_prettify.
        '''
        odtchomp.PROTECTED_NAMES = ["evolver_prot"]
        name = 'evolver_prot:givenName:quantity'
        uniquenessCheck = [['evolver_prot', 'givenName', 'quantity'], ['evolver2', 'givenName2', 'quantity']]
        new_name = odtchomp.namepolish(name, uniquenessCheck)
        self.assertEqual(new_name, 'givenName evolver_prot quantity')

    def test6_evolver_quantity(self):
        '''
        Name polish is called by headers_prettify.
        '''
        name = 'evolver::quantity'
        uniquenessCheck = [['evolver', '','quantity'], ['evolver', '', 'quantity']]
        new_name = odtchomp.namepolish(name, uniquenessCheck)
        self.assertEqual(new_name, 'evolver quantity')

    def test_remove_evolver_prefix(self):
        '''
        Name polish is called by headers_prettify.
        '''
        name = 'Oxs_evolver::quantity'
        uniquenessCheck = [['Oxs_evolver', '','quantity'], ['Oxs_evolver', '', 'quantity']]
        new_name = odtchomp.namepolish(name, uniquenessCheck)
        self.assertEqual(new_name, 'evolver quantity')
        
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
        print(len(ret))
        # If the length of 'ret' is more than 1, it means that there is a 
        # duplicate of the target item in the indicated position.
        # It seems to be called 'filter on pos' as it returns lists only
        # if the target value is found in the position specified within
        # the lists supplied.
        self.assertEqual(ret, [['item1', 'item2', 'item3'], ['item1', 'item5', 'item6']])
        
    def test_filterOnPos_item_in_one_of_two_sublists(self):
        '''
        Target item found in specified position in one of the input lists.
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
        
class Test_prefix_punt(unittest.TestCase):
    def test_prefix_punt_no_element(self):
        data = "Oxs_"
        prefix = odtchomp.prefix_punt(data)
        self.assertEqual(prefix, "")
        
    def test_prefix_punt_an_element(self):
        data = "Oxs_prefix"
        prefix = odtchomp.prefix_punt(data)
        self.assertEqual(prefix, "prefix")
        
class Test_Interpreter(unittest.TestCase):
        """
        """
        
        def setUp(self):
            self.interpreter = odtchomp.Interpreter({'key1 part1 part2': 'Zed', 'key2 part1 part2': 39, 'key3 part1 part2': 9}, ['key1 part1 part2', 'key2 part1 part2', 'key3 part1 part2'])
        
           
        def test_getNames(self):
            keys = self.interpreter.getNames()
            self.assertEqual(keys, ['key1 part1 part2', 'key2 part1 part2', 'key3 part1 part2'])
        
        def test_getData(self):
            data = self.interpreter.getData()
            self.assertEqual(data, {'key1 part1 part2': 'Zed', 'key2 part1 part2': 39, 'key3 part1 part2': 9})
            
        def test_getDataLength(self):
            dataLength = self.interpreter.getDataLength()
            self.assertEqual(dataLength, 3)
            
        def test_mismatched_keys_and_dict(self):
            # It seems like Interpreter assumes that keys and dict are 'matched'
            # as they are in the above tests. It may be possible for them to
            # not be matched, and it would be good to test for behaviour in that
            # case.
            pass
            
class Test_chomp(unittest.TestCase):
    """
    """
    def test_chomp(self):
        pass
        
class Test_log(unittest.TestCase):
    """
    log(str) is just a simple print function at the moment.
    It could potentially be exented to more complete logging outputs, so I want
    to put in some initial tests.
    """
    def test_print_to_console(self):
        capturedOutput = StringIO.StringIO()          # Create StringIO object
        sys.stdout = capturedOutput                   #  and redirect stdout.
        odtchomp.log('test')                          # Call unchanged function.
        self.assertEqual(capturedOutput.getvalue(), 'test\n')
        sys.stdout = sys.__stdout__                   # Reset redirect.
        
class Test_write(unittest.TestCase):
    """
    File IO etc.
    """
    def test_write(self):
        pass
        
class Test_resolve(unittest.TestCase):
    """
    """
    def test_resolve(self):
        pass
        
class Test_split_densify(unittest.TestCase):
    """
    """
    def test_split_densify(self):
        pass
        
        