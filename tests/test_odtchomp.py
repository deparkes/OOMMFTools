from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
import sys, os
import io
import tempfile
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
sys.path.insert(0, PROJECT_DIR)

import unittest
from oommftools.core import odtchomp
import numpy as np
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
            
        def test_values_as_list(self):
            # This is how the data is stored for real.
            pass
            
class Test_chomp(unittest.TestCase):
    """
    """

    def setUp(self):
        with tempfile.NamedTemporaryFile(delete=False) as self.temp:
            # odt output file from /local_tests/2dpbc_film.odt
            self.temp.write('# ODT 1.0\n# Table Start\n# Title: mmArchive Data Table, Thu Dec 15 01:13:45 EST 2011\n# Columns: {Oxs_EulerEvolve::Total energy} {Oxs_EulerEvolve::Energy calc count} {Oxs_EulerEvolve::Max dm/dt} Oxs_EulerEvolve::dE/dt {Oxs_EulerEvolve::Delta E} PBC_Exchange_2D::Energy PBC_Demag_2D::Energy Oxs_TimeDriver::Iteration {Oxs_TimeDriver::Stage iteration} Oxs_TimeDriver::Stage Oxs_TimeDriver::mx   Oxs_TimeDriver::my   Oxs_TimeDriver::mz   {Oxs_TimeDriver::Last time step} {Oxs_TimeDriver::Simulation time}\n# Units:                  J                                 {}                             deg/ns                     J/s                       J                         J                     J                      {}                            {}                          {}                   {}                   {}                   {}                          s                                 s                \n                 0                                  1                                0                         0                        0                        0                      0                      0                             0                           0                     1                    0                    0                          0                                0                         \n# Table End\n'.encode())
            self.temp.flush()

        with tempfile.NamedTemporaryFile(delete=False) as self.temp_multiline:
            # odt output file from /local_tests/cgtest_qdemag.odt
            self.temp_multiline.write("# ODT 1.0\n# Table Start\n# Title: mmArchive Data Table, Wed Aug 17 23:55:57 EDT 2011\n# Columns: {Oxs_CGEvolve::Max mxHxm} {Oxs_CGEvolve::Total energy} {Oxs_CGEvolve::Delta E} {Oxs_CGEvolve::Bracket count} {Oxs_CGEvolve::Line min count} {Oxs_CGEvolve::Conjugate cycle count} {Oxs_CGEvolve::Cycle count} {Oxs_CGEvolve::Cycle sub count} {Oxs_CGEvolve::Energy calc count} Oxs_UniformExchange::Energy {Oxs_UniformExchange::Max Spin Ang} {Oxs_UniformExchange::Stage Max Spin Ang} {Oxs_UniformExchange::Run Max Spin Ang} Oxs_UZeeman::Energy  Oxs_UZeeman::B       Oxs_UZeeman::Bx      Oxs_UZeeman::By      Oxs_UZeeman::Bz      Oxs_QDemag::Energy   Oxs_MinDriver::Iteration {Oxs_MinDriver::Stage iteration} Oxs_MinDriver::Stage Oxs_MinDriver::mx    Oxs_MinDriver::my    Oxs_MinDriver::mz   \n# Units:              A/m                         J                          J                         {}                             {}                                {}                               {}                            {}                               {}                              J                              deg                                    deg                                      deg                            J                 mT                   mT                   mT                   mT                     J                       {}                           {}                         {}                 {}                   {}                   {}           \n              1746207.4553428555          3.217924418664379e-16       3.217924418664379e-16        0                              0                                 1                                1                             1                                1                              1.5600000000000002e-16             90                                     90                                       90                             0                    0                    0                    0                    0                    1.6579244186643904e-16    0                            0                          0                    0                    0                    0.093333333333333338\n              1744975.7833005877          3.215582194547401e-16      -2.3422241169780424e-19        1                              0                                 1                                1                             1                                2                              1.557651828520484e-16             89.922852335181432                     90                                       90                             0                    0                    0                    0                    0                    1.6579303660269022e-16    1                            1                          0                   -1.531614341527327e-22  3.0681904819276596e-18  0.093339189685331531\n              1736217.8420609126          3.199236505077561e-16      -1.6345689469839961e-18        2                              0                                 1                                1                             1                                3                              1.541270134531275e-16             89.382653405546762                     90                                       90                             0                    0                    0                    0                    0                    1.657966370546301e-16    2                            2                          0                   -2.5491115391357905e-21  1.4513110121091206e-18  0.093379696220933367\n              1736798.4776375247          3.1992382281547448e-16       1.723077183773465e-22        2                              0                                 2                                2                             2                                4                              1.541270134531275e-16             89.382653405546762                     89.382653405546762                       90                             2.350988701644575e-38  25                   25                   0                    0                    1.6579680936234491e-16    3                            0                          1                   -2.5491115391357905e-21  1.4513110121091206e-18  0.093379696220933367\n              1735542.5302981746          3.19690540828253e-16      -2.3328198722148531e-19        3                              0                                 2                                2                             0                                5                              1.5389400794809783e-16             89.305549519311413                     89.382653405546762                       90                            -7.1971516238468971e-22  25                   25                   0                    0                    1.657972525953178e-16    4                            1                          1                    9.9960439220095185e-06 -1.1641532182693482e-19  0.093385435223110741\n              1726615.2345995705          3.1806259169067142e-16      -1.6279491375815754e-18        4                              0                                 2                                2                             0                                6                              1.5226855960236189e-16             88.765671856133352                     89.382653405546762                       90                            -5.7577146745565936e-21  25                   25                   0                    0                    1.6579978980298341e-16    5                            2                          1                    7.9968259368841892e-05 -2.276566293504503e-19  0.093425117917793343\n              1727456.1584240147          3.1805700692414893e-16      -5.5847665224947569e-21        4                              0                                 3                                3                             1                                7                              1.5226855960236189e-16             88.765671856133352                     88.765671856133352                       90                            -1.1515429349113187e-20  50                   50                   0                    0                    1.6579996275113541e-16    6                            0                          2                    7.9968259368841892e-05 -2.276566293504503e-19  0.093425117917793343\n              1726177.0394015557          3.178232423469609e-16      -2.3376457718802646e-19        5                              0                                 3                                3                             0                                8                              1.5203740114081541e-16             88.688628007966074                     88.765671856133352                       90                            -1.4410330576843686e-20  50                   50                   0                    0                    1.6580025153672314e-16    7                            1                          2                    0.00010007174011696985  2.3800465795728893e-19  0.09343073591332593\n              1717088.1918065522          3.1619194720246485e-16      -1.6312951444960488e-18        6                              0                                 3                                3                             0                                9                              1.5042491867273622e-16             88.14918477645486                      88.765671856133352                       90                            -3.4674600281125716e-20  50                   50                   0                    0                    1.658017031300097e-16    8                            2                          2                    0.00024079583528559552 -6.3381675216886729e-19  0.093469568768023481\n# Table End".encode())
            self.temp_multiline.flush()


    def test_chomp_headers(self):
        chomper = odtchomp.chomp(self.temp.name)
        test_output = ['Total energy', 'Energy calc count', 'Max dm/dt', 'dE/dt', 'Delta E', 'PBC_Exchange_2D Energy', 'PBC_Demag_2D Energy', 'Iteration', 'Stage iteration', 'Stage', 'mx', 'my', 'mz', 'Last time step', 'Simulation time']
        self.assertEqual(chomper.getNames(), test_output)

    def test_chomp_data(self):
        #chomper = odtchomp.chomp(f.name)
        chomper = odtchomp.chomp(self.temp.name)
        test_output = {'Delta E': np.array([ 0.]), 
                        'Energy calc count': np.array([ 1.]), 
                        'Stage iteration': np.array([ 0.]),
                        'Simulation time': np.array([ 0.]), 
                        'Iteration': np.array([ 0.]), 
                        'Last time step': np.array([ 0.]), 
                        'PBC_Demag_2D Energy': np.array([ 0.]), 
                        'PBC_Exchange_2D Energy': np.array([ 0.]), 
                        'Max dm/dt': np.array([ 0.]), 
                        'dE/dt': np.array([ 0.]), 
                        'Stage': np.array([ 0.]), 
                        'my': np.array([ 0.]), 
                        'mx': np.array([ 1.]), 
                        'Total energy': np.array([ 0.]), 
                        'mz': np.array([ 0.])}
        self.assertDictEqual(chomper.getData(), test_output)

    def test_chomp_length_data(self):
        chomper = odtchomp.chomp(self.temp.name)
        test_output = "1"
        self.assertEqual(str(chomper.getDataLength()), test_output)

    def test_chomp_length_data_multiline(self):
        chomper = odtchomp.chomp(self.temp_multiline.name)
        test_output = "9"
        self.assertEqual(str(chomper.getDataLength()), test_output)

    def test_chomp_absolute_path(self):
        """
        There seemed to be a problem with loading files from abolute path
        """
        pass
        
    def test_chomp_with_parent(self):
        """
        There is the capability to load in from wx widget
        """
        pass
        
class Test_log(unittest.TestCase):
    """
    log(str) is just a simple print function at the moment.
    It could potentially be exented to more complete logging outputs, so I want
    to put in some initial tests.
    """
    def test_print_to_console(self):
        capturedOutput = io.StringIO()          # Create StringIO object
        sys.stdout = capturedOutput                   #  and redirect stdout.
        odtchomp.log('test')                          # Call unchanged function.
        self.assertEqual(capturedOutput.getvalue(), 'test\n')
        sys.stdout = sys.__stdout__                   # Reset redirect.
        
class Test_write(unittest.TestCase):
    """
    File IO etc.
    """
    def setUp(self):
        self.interpreter = odtchomp.Interpreter({'key1 part1 part2': [1,2,3], 'key2 part1 part2': [4,5,6], 'key3 part1 part2': [7,8,9]}, ['key1 part1 part2', 'key2 part1 part2', 'key3 part1 part2'])
    
    
    def test_write_print_to_screen(self):
        pass
    
    def test_write_cleanup(self):
        pass
    
    def test_write_log(self):
        pass
        
    def test_write_outfile(self):
        """
        Not sure if this is dropping a line from the end...
        """
        outfile = tempfile.mkstemp()[1]
        # NOTE: Alternatively, for Python 2.6+, you can use
        # tempfile.SpooledTemporaryFile, e.g.,
        #outfile = tempfile.SpooledTemporaryFile(10 ** 9)
        odtchomp.write(outfile, self.interpreter, ",", ["key1 part1 part2", "key2 part1 part2", "key3 part1 part2"])
        with open(outfile) as f:
            content = f.read()
        self.assertEqual(content, "key1 part1 part2, key2 part1 part2, key3 part1 part2\n1, 4, 7\n2, 5, 8\n")
        
class Test_resolve(unittest.TestCase):
    """
    """
    def test_resolve_single_key(self):
        out = odtchomp.resolve({"key": "value"}, ["key"])
        self.assertEqual(out, ["value"])
        
    def test_resolve_two_keys(self):
        out = odtchomp.resolve({"key1": "value1", "key2": "value2"}, ["key1", "key2"])
        self.assertEqual(out, ["value1", "value2"])
        
class Test_split_densify(unittest.TestCase):
    """
    """
    def test_split_densify_default_delim(self):
        rets = odtchomp.split_densify("word1 word2 word3")
        self.assertEqual(rets, ["word1", "word2", "word3"])

    def test_split_densify_extra_whitespace(self):
        rets = odtchomp.split_densify("word1\t word2  word3")
        self.assertEqual(rets, ["word1", "word2", "word3"])
        
    def test_split_densify_tab_delim(self):
        rets = odtchomp.split_densify("word1\tword2\tword3", "\t")
        self.assertEqual(rets, ["word1", "word2", "word3"])        