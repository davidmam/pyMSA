# Copyright (c) 2012 - N.P. de Klein
#
#     This file is part of Python Mass Spec Analyzer (PyMSA).
#
#     Python Mass Spec Analyzer (PyMSA) is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Python Mass Spec Analyzer (PyMSA) is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Python Mass Spec Analyzer (PyMSA).  If not, see <http://www.gnu.org/licenses/>.")

"""
Unit test of rFunctions.py
"""

# author: ndeklein
# date:10/02/2012
# summary: Unit testing functionality of the rFunctions.py script

import sys
import os
# to be able to import unittest2 from a locally installed unittest2     * REMOVE WHEN SENDING TO OTHER USERS *
try:
    sys.path.append('/homes/ndeklein/python2.6/site-packages')
except:
    pass# some magic to import from pyMS. dirname(dirname(__file__)) gets the two directories closer to the root.
# this is so that pyMS is added to the pythonpath and you can do import rFunctions.py
# if this is made in a package from pyMS import rFunctions should also work
dirname = os.path.dirname
sys.path.append(os.path.join(dirname(dirname(__file__))))

import config
import rFunctions
import rpy2.robjects as R

import unittest2 as unittest


configHandle =  config.ConfigHandle()
config = configHandle.getConfig()
testFolder = os.path.join(os.path.dirname(__file__), config.get('test','testfilefolder'))


class testRFunctions(unittest.TestCase):
    """
    A test class for the output module.
    """

    def test_index(self):
        expectedIndex = 1
        
        # testing dataframe
        dict = {'test1': R.IntVector((12,12,15)), 'test2': R.IntVector((32,4,12)), 'test3': R.IntVector((3,12,26))}       # note that test1 has 12 in row 1 and row 2 
        testFrame = R.DataFrame(dict)    
        # because the dict from which the dataframe is made is not ordened, the testframe is ordened first to make sure that the column 'test2' is always at the same position
        # however, to do tis I'm using the index function that I'm testing, which might or might not be a right thing to do
        testFrame = testFrame.rx[True, R.r['with'](testFrame, R.r['order'](R.IntVector([rFunctions.index(testFrame, 'test1'), rFunctions.index(testFrame, 'test2'), rFunctions.index(testFrame, 'test3')])),)]

        actualDataFrameIndex = rFunctions.index(testFrame, 'test2')
        # testing matrix (same values as the dataframe)
        testMatrix = R.r.matrix(R.IntVector([12,12,15,32,4,12,3,12,26]), nrow=3)
        testMatrix.colnames = R.StrVector(['test1', 'test2','test3'])
        actualMatrixIndex = rFunctions.index(testMatrix, 'test2')

        self.assertEqual(expectedIndex, actualDataFrameIndex)
        self.assertEqual(expectedIndex, actualMatrixIndex)

    def test_indexException(self):
        # testing dataframe
        dict = {'test1': R.IntVector((12,12,15)), 'test2': R.IntVector((32,4,12)), 'test3': R.IntVector((3,12,26))}       # note that test1 has 12 in row 1 and row 2 
        testFrame = R.DataFrame(dict)    
        # because the dict from which the dataframe is made is not ordened, the testframe is ordened first to make sure that the column 'test2' is always at the same position
        # however, to do tis I'm using the index function that I'm testing, which might or might not be a right thing to do
        testFrame = testFrame.rx[True, R.r['with'](testFrame, R.r['order'](R.IntVector([rFunctions.index(testFrame, 'test1'), rFunctions.index(testFrame, 'test2'), rFunctions.index(testFrame, 'test3')])),)]

        actualDataFrameIndex = rFunctions.index(testFrame, 'test2')

        self.assertRaises(KeyError, rFunctions.index,testFrame, 'column_notindf')
   

    def test_getRowsWithUniqColumn(self):
        
        expectedDict = {'test1': R.IntVector((12,15)), 'test2': R.IntVector((32,12)), 'test3': R.IntVector((3,26))}  
        expectedSubset = R.DataFrame(expectedDict)
        # because the dict from which the dataframe is made is not ordened, the testframe is ordened first to make sure that the column 'test2' is always at the same position
        expectedSubset = expectedSubset.rx[True, R.r['with'](expectedSubset, R.r['order'](R.IntVector([rFunctions.index(expectedSubset, 'test1'), rFunctions.index(expectedSubset, 'test2'), rFunctions.index(expectedSubset, 'test3')])),)]


        testDict = {'test1': R.IntVector((12,12,15)), 'test2': R.IntVector((32,4,12)), 'test3': R.IntVector((3,12,26))}       # note that test1 has 12 in row 1 and row 2 

        # testing dataframe
        testFrame = R.DataFrame(testDict)    
        # because the dict from which the dataframe is made is not ordened, the testframe is ordened first to make sure that the column 'test2' is always at the same position
        testFrame = testFrame.rx[True, R.r['with'](testFrame, R.r['order'](R.IntVector([rFunctions.index(testFrame, 'test1'), rFunctions.index(testFrame, 'test2'), rFunctions.index(testFrame, 'test3')])),)]
        actualDfSubset = rFunctions.getRowsWithUniqColumn(testFrame, 'test1')            # now only two of the three rows remain, because test1 had 12 twice in the row
        
        # a list to keep track of the results, can't compare two dataframes directly so want to compare their values only
        expectedResultList = []
        actualResultList = []
        # getting the relevant data from both expected and actual subset. 
        for values in expectedSubset.iteritems():
            # and append them to the list
            expectedResultList.append([values[0],values[1][0], values[1][1]])
        for values in actualDfSubset.iteritems():
            actualResultList.append([values[0],values[1][0], values[1][1]])
    
        self.assertEqual(expectedResultList, actualResultList)
    
    def test_getRowsWithUniqColumnException(self):
        # testing dataframe
        dict =  {'test1': R.IntVector((12,12,15)), 'test2': R.IntVector((32,4,12)), 'test3': R.IntVector((3,12,26))} 
        testFrame = R.DataFrame(dict)    
        self.assertRaises(TypeError, rFunctions.getRowsWithUniqColumn, testFrame, {'nota':'strType'})
        self.assertRaises(KeyError, rFunctions.getRowsWithUniqColumn, testFrame, 'notAcolumnName')

    def test_getColumns(self):
        # the dict of whcih the dataframe is made to give to pass to the function, and of which the expected
        # subset is made:
        expectedDict = {'test1': R.IntVector((12,12,15)), 'test3': R.IntVector((3,12,26))} 
        expectedSubset = R.DataFrame(expectedDict)
        # note that expectedDict is the same as testDict, but misses the test2 vector
        testDict = {'test1': R.IntVector((12,12,15)), 'test2': R.IntVector((32,4,12)), 'test3': R.IntVector((3,12,26))}
        # testing dataframe
        testFrame = R.DataFrame(testDict)    
        # because the dict from which the dataframe is made is not ordened, the testframe is ordened first to make sure that the column 'test2' is always at the same position
        testFrame = testFrame.rx[True, R.r['with'](testFrame, R.r['order'](R.IntVector([rFunctions.index(testFrame, 'test1'), rFunctions.index(testFrame, 'test2'), rFunctions.index(testFrame, 'test3')])),)]
        actualDfSubset = rFunctions.getColumns(testFrame, 'test1', 'test3')            # now only two of the three rows remain, because test1 had 12 twice in the row

        # a list to keep track of the results, can't compare two dataframes directly so want to compare their values only
        expectedResultList = []
        actualResultList = []
        # getting the relevant data from both expected and actual subset. 
        for values in expectedSubset.iteritems():
            # and append them to the list
            expectedResultList.append([values[0],values[1][0], values[1][1]])
        for values in actualDfSubset.iteritems():
            actualResultList.append([values[0],values[1][0], values[1][1]])
        self.assertEqual(expectedResultList, actualResultList)
    
    def test_getColumnsException(self):
        dict = {'test1':R.IntVector((12,15)), 'test2':R.IntVector((32,12)), 'test3':R.IntVector((3,26))}
        testFrame = R.DataFrame(dict)
        # testing dataframe
        testFrame = R.DataFrame(dict)    
        # because the dict from which the dataframe is made is not ordened, the testframe is ordened first to make sure that the column 'test2' is always at the same position
        testFrame = testFrame.rx[True, R.r['with'](testFrame, R.r['order'](R.IntVector([rFunctions.index(testFrame, 'test1'), rFunctions.index(testFrame, 'test2'), rFunctions.index(testFrame, 'test3')])),)]
        
        self.assertRaises(TypeError, rFunctions.getColumns, testFrame)
        self.assertRaises(TypeError, rFunctions.getColumns, testFrame, 'test1', 1)  
        self.assertRaises(TypeError, rFunctions.getColumns, testFrame,  1, 'test1')  
        self.assertRaises(TypeError, rFunctions.getColumns, [[1,2,3],[3,2,2],[4,3,2]], 'test1')
        
    def test_takeLog(self):
        # because of rounding issues after 7 numbers after the comma I round both expected and actual to an int
        expectedLogVector = R.IntVector((5.0, 5.0, 4.0, 5.0, 5.0, 5.0, 3.0, 5.0))
        expectedLogList = []
        # you can't compare vectors directly because this part >> Python:0x12241f80 << is always different, I transform them to lists first
        for value in expectedLogVector:
            expectedLogList.append(value)
        
        vector = R.IntVector((59843, 34982, 12425, 90534, 34532, 54642, 1239, 43534))
        actualLogVector = R.r['round'](rFunctions.takeLog(vector, 10))
        actualLogList = []
        for value in actualLogVector:
            actualLogList.append(value)
        
        self.assertEqual(expectedLogList, actualLogList)
        
    def test_takeLogException(self):
        vector = R.IntVector((59843, 34982, 12425, 90534, 34532, 54642, 1239, 43534))
        self.assertRaises(ValueError, rFunctions.takeLog, vector, -2)
        

    def test_readCsvFile(self):
        self.assertIsInstance(rFunctions.readCsvFile(testFolder+'feature.csv'), R.vectors.DataFrame)

    def test_readCsvFileExceptions(self):
        self.assertRaises(IOError, rFunctions.readCsvFile, 'fakefile')
        self.assertRaises(TypeError, rFunctions.readCsvFile, testFolder+'feature.csv', head='not a bool')


    def test_fillNA(self):
        expectedList_1 = [1,2,3, R.NA_Integer, R.NA_Integer]
        expectedList_2 = [1,2,3]
        
        actualList_1 = rFunctions.fillNA([1,2,3], 2, 'NA_Integer')
        # this should not add any values, because amount is lower than 0.
        actualList_2 = rFunctions.fillNA([1,2,3], -2, 'NA_Integer')
        
        self.assertListEqual(expectedList_1, actualList_1)
        self.assertListEqual(expectedList_2, actualList_2)
        
    def test_fillNAException(self):
        lst = [1,2,3]
        self.assertRaises(TypeError, rFunctions.fillNA, 'not a list',4, 'NA_Integer')
        self.assertRaises(TypeError, rFunctions.fillNA, lst, 'not an int', 'NA_Integer')
        self.assertRaises(TypeError, rFunctions.fillNA, lst, 4, 'Not allowed')

def suite():
    suite = unittest.TestSuite()
    # adding the unit tests to the test suite
    suite.addTest(unittest.makeSuite(testRFunctions))
    return suite

unittest.TextTestRunner(verbosity=2).run(suite())
