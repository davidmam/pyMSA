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
Unit test of featureMapping.py
"""

# author: ndeklein
# date:10/02/2012
# summary: Unit testing functionality of the featureMapping.py script


import sys 
import os
# to be able to import unittest2 from a locally installed unittest2     * REMOVE WHEN SENDING TO OTHER USERS *
try:
    sys.path.append('/homes/ndeklein/python2.6/site-packages')
except:
    pass# some magic to import from pyMS. dirname(dirname(__file__)) gets the two directories closer to the root.
# this is so that pyMS is added to the pythonpath and you can do import parseFeatureXML.py
# if this is made in a package from pyMS import parseFeatureXML should also work
dirname = os.path.dirname
sys.path.append(os.path.join(dirname(dirname(__file__))))
import unittest2 as unittest
import config
import parseFeatureXML
import featureMapping as fm


configHandle =  config.ConfigHandle()
config = configHandle.getConfig()
testFolder = os.path.join(os.path.dirname(__file__), config.get('test','testfilefolder'))
import warnings

class testFeatureMapping(unittest.TestCase):
    """
    A test class for the output module.
    
    """
    def setUp(self):

        """

        set up data used in the tests.

        setUp is called before each test function execution.

        """
        warnings.filterwarnings('ignore')
    
    def test_FeatureMappingException(self):
        featureXML_1 = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
        featureXML_2 = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_2.featureXML')
        trafoXML = testFolder+'featurexmlTestFile_1.trafoXML'
        trafoXML_2 = testFolder+'featurexmlTestFile_2.trafoXML'
        self.assertRaises(IOError, fm.Map, featureXML_1, featureXML_2, trafoXML)
        self.assertRaises(RuntimeError, fm.Map, featureXML_2, featureXML_2, trafoXML_2)
    
    def test_mapping(self):
        expectedDict = {'featureXML_1_mapped': set(['4009.58726', '5107.29224', '5109.29224']),
                         'featureXML_1_not_mapped': set(['7052.29224']),
                         'featureXML_2_mapped': set(['3969.58726', '5189.29224', '5197.29224']),
                         'featureXML_2_not_mapped': set(['5345.29224'])}
                               
        
        featureXML_1 = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
        featureXML_2 = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_2.featureXML')
        trafoXML = testFolder+'featurexmlTestFile_2.trafoXML'
        featureMapping = fm.Map(featureXML_1, featureXML_2, trafoXML)
        actualDict = featureMapping.mapping()
        
        
        self.assertDictEqual(expectedDict, actualDict)
    
    def test_getMappedFeatureIds(self):
        expectedList =  [{'from': 5189.2922399999998,'from_featureID': 'f_13020522388175237334', 'to': 5109.2922399999998,
                          'to_featureID': 'f_13020522388175237334'},  {'from': 5197.2922399999998,'from_featureID': 'f_43922326584371237334',
                          'to': 5107.2922399999998, 'to_featureID': 'f_43922326584371237334'},{'from': 3969.5872599999998,'from_featureID': 'f_8613715360396561740',
                          'to': 4009.5872599999998, 'to_featureID': 'f_8613715360396561740'}]
               
        featureXML_1 = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
        featureXML_2 = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_2.featureXML')
        trafoXML = testFolder+'featurexmlTestFile_2.trafoXML'
        featureMapping = fm.Map(featureXML_1, featureXML_2, trafoXML)
        actualList = featureMapping.getMappedFeatureIds()
        
        
        self.assertListEqual(expectedList, actualList)   
    
    def test_unmappedIntensities(self):
        expectedList_1 = ['52234']
        expectedList_2 = ['524284']
        
        featureXML_1 = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
        featureXML_2 = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_2.featureXML')
        trafoXML = testFolder+'featurexmlTestFile_2.trafoXML'
        featureMapping = fm.Map(featureXML_1, featureXML_2, trafoXML)
        actualList_1, actualList_2 = featureMapping.unmappedIntensities()
    
        self.assertListEqual(expectedList_1, actualList_1)
        self.assertListEqual(expectedList_2, actualList_2)
    
    def test_mappedIntensities(self):
        expectedList_1 = ['556384', '234284', '111429']
        expectedList_2 = ['111329', '524284', '524284']
        
        featureXML_1 = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
        featureXML_2 = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_2.featureXML')
        trafoXML = testFolder+'featurexmlTestFile_2.trafoXML'
        featureMapping = fm.Map(featureXML_1, featureXML_2, trafoXML)        
        actualList_1, actualList_2 = featureMapping.mappedIntensities()
        
        self.assertListEqual(expectedList_1, actualList_1)
        self.assertListEqual(expectedList_2, actualList_2)
        
def suite():
    suite = unittest.TestSuite()
    # adding the unit tests to the test suite
    suite.addTest(unittest.makeSuite(testFeatureMapping))
    return suite

