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
Unit test of compareFeatureXMLmzML.py
"""

# author: ndeklein
# date:10/02/2012
# summary: Unit testing functionality of the compareFeatureXMLmzML.py script


import sys 
import os
import doctest
# to be able to import unittest2 from a locally installed unittest2    
try:
    sys.path.append('/homes/ndeklein/python2.6/site-packages')
except:
    pass
# some magic to import from pyMS. dirname(dirname(__file__)) gets the two directories closer to the root.
# this is so that pyMS is added to the pythonpath and you can do import compareFeatureXMLmzML.py
# if this is made in a package from pyMS import compareFeatureXMLmzML should also work
dirname = os.path.dirname
sys.path.append(os.path.join(dirname(dirname(__file__))))
import unittest2 as unittest
import compareFeatureXMLmzML as compare
import config
configHandle =  config.ConfigHandle()
config = configHandle.getConfig()
testFolder = os.path.join(os.path.dirname(__file__), config.get('test','testfilefolder'))


class testCompareFeatureXMLmzML(unittest.TestCase):
    """
    A test class for the compareFeatureXMLmzML module.
    """

        
    def test_compareCoordinate(self):
        expectedCsvRead = ['id','# precursors\r\nf_43922326584371237334','1\r\nf_130205234428175237334','0\r\nf_8613715360396561740','0\r\nf_13020522388175237334','1\r\n']     # this is the expected output of reading the output csv file
        expectedReturnValue = {'totalPrecursorsInFeatures':2, 'averagePrecursorsInFeatures':0.5, 'featPerPrecursorDict':{'f_13020522388175237334': 1, 'f_130205234428175237334': 0, 'f_43922326584371237334': 1, 'f_8613715360396561740': 0}}
        
        # to make sure that the test isn't passing when the method doesn't work, but the file already exists
        # the file is deleted at the beginning of the test rather than at the end, because user might want to check how an example output file looks
        if os.path.exists(testFolder+'testPrecursorPerFeature.csv'): 
            os.remove(testFolder+'testPrecursorPerFeature.csv') 
            
        actualReturnValue = compare.compareCoordinate(testFolder+'mzml_test_file_1.mzML', testFolder+'featurexmlTestFile_1.featureXML', True, testFolder+'testPrecursorPerFeature.csv')
        csvFile =  open(testFolder+'testPrecursorPerFeature.csv')        
        csvRead = csvFile.read().split('\t')
        
        
        self.assertDictEqual(expectedReturnValue, actualReturnValue)
        self.assertListEqual(expectedCsvRead, csvRead)
        
        if os.path.exists(testFolder+'testPrecursorPerFeature.csv'): 
            os.remove(testFolder+'testPrecursorPerFeature.csv') 


def suite():
    suite = unittest.TestSuite()
    # adding the unit tests to the test suite
    suite.addTest(unittest.makeSuite(testCompareFeatureXMLmzML))
    return suite

unittest.TextTestRunner(verbosity=2).run(suite())
