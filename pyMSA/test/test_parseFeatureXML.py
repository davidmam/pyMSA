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
Unit test of parseFeatureXML.py
"""

# author: ndeklein
# date:10/02/2012
# summary: Unit testing functionality of the parseFeatureXML.py script


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
import collections

configHandle =  config.ConfigHandle()
config = configHandle.getConfig()
testFolder = config.get('test','testfilefolder')


class testParseFeatureXML(unittest.TestCase):
    """
    A test class for the output module.
    """
    
    def test_Reader(self):
        expectedDict = {'f_43922326584371237334': {'convexhull': [{'rt': '5107.9217', 'mz': '337.125209180674'}, {'rt': '5108.7642', 'mz': '337.124751115092'}, {'rt': '5109.6031', 'mz': '337.124841989895'}, {'rt': '5110.4848', 'mz': '337.12529301464'}, {'rt': '5112.6874', 'mz': '337.124957942644'}, {'rt': '5111.6874', 'mz': '339.251041063348'}, {'rt': '5110.4848', 'mz': '339.251376135343'}, {'rt': '5109.6031', 'mz': '339.250925110599'}, {'rt': '5108.7642', 'mz': '339.250834235796'}, {'rt': '5108.9217', 'mz': '339.251292301377'}], 'intensity': '556384', 'content': '\n\t\t\t', 'charge': '2', 'overallquality': '225053', 'userParam': [{'type': 'int', 'name': 'spectrum_index', 'value': '3916'}, {'type': 'string', 'name': 'spectrum_native_id', 'value': 'controllerType=0 controllerNumber=1 scan=18484'}], 'retention time': '5107.29224', 'quality': [[('dim', '0'), '0'], [('dim', '1'), '0']], 'mz': 337.25110482479602}, 'f_130205234428175237334': {'convexhull': [{'rt': '7052.9217', 'mz': '336.125209180674'}, {'rt': '7051.2924', 'mz': '336.124751115092'}, {'rt': '7053.4848', 'mz': '336.124841989895'}, {'rt': '7052.6874', 'mz': '336.12529301464'}, {'rt': '7048.9224', 'mz': '336.124957942644'}, {'rt': '7045.7642', 'mz': '338.251041063348'}, {'rt': '7053.4848', 'mz': '338.251376135343'}, {'rt': '7051.7642', 'mz': '338.250925110599'}, {'rt': '7052.6874', 'mz': '338.250834235796'}, {'rt': '7050.9217', 'mz': '338.251292301377'}], 'intensity': '52234', 'content': '\n\t\t\t', 'charge': '2', 'overallquality': '225053', 'userParam': [{'type': 'int', 'name': 'spectrum_index', 'value': '421'}, {'type': 'string', 'name': 'spectrum_native_id', 'value': 'controllerType=0 controllerNumber=1 scan=5342'}], 'retention time': '7052.29224', 'quality': [[('dim', '0'), '0'], [('dim', '1'), '0']], 'mz': 322.25110482479602}, 'f_8613715360396561740': {'convexhull': [{'rt': '4001.7973', 'mz': '428.071338720547'}, {'rt': '4004.4017', 'mz': '428.071177661641'}, {'rt': '4009.2555', 'mz': '428.071136832932'}, {'rt': '4014.7713', 'mz': '428.071491868401'}, {'rt': '4017.7105', 'mz': '428.070943557216'}, {'rt': '4017.7105', 'mz': '430.19702667792'}, {'rt': '4014.7713', 'mz': '430.197574989105'}, {'rt': '4009.2555', 'mz': '430.197219953635'}, {'rt': '4004.4017', 'mz': '430.197260782345'}, {'rt': '4001.7973', 'mz': '430.197421841251'}], 'intensity': '111429', 'content': '\n\t\t\t', 'charge': '2', 'overallquality': '35753.2', 'userParam': [{'type': 'int', 'name': 'spectrum_index', 'value': '2895'}, {'type': 'string', 'name': 'spectrum_native_id', 'value': 'controllerType=0 controllerNumber=1 scan=15394'}], 'retention time': '4009.58726', 'quality': [[('dim', '0'), '0'], [('dim', '1'), '0']], 'mz': 428.19727599723802}, 'f_13020522388175237334': {'convexhull': [{'rt': '5105.9217', 'mz': '336.125209180674'}, {'rt': '5108.7642', 'mz': '336.124751115092'}, {'rt': '5109.6031', 'mz': '336.124841989895'}, {'rt': '5110.4848', 'mz': '336.12529301464'}, {'rt': '5111.6874', 'mz': '336.124957942644'}, {'rt': '5111.6874', 'mz': '338.251041063348'}, {'rt': '5110.4848', 'mz': '338.251376135343'}, {'rt': '5109.6031', 'mz': '338.250925110599'}, {'rt': '5108.7642', 'mz': '338.250834235796'}, {'rt': '5105.9217', 'mz': '338.251292301377'}], 'intensity': '234284', 'content': '\n\t\t\t', 'charge': '2', 'overallquality': '225053', 'userParam': [{'type': 'int', 'name': 'spectrum_index', 'value': '3916'}, {'type': 'string', 'name': 'spectrum_native_id', 'value': 'controllerType=0 controllerNumber=1 scan=18484'}], 'retention time': '5109.29224', 'quality': [[('dim', '0'), '0'], [('dim', '1'), '0']], 'mz': 336.25110482479602}}
                
        featureXML = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
        keys =  featureXML.getKeys()
        features = featureXML.getSimpleFeatureInfo()
        actualDict = collections.defaultdict(dict)
        for feature in features:
            for key in keys:
                if key != 'id':  # because the id will be used as the key of dictionary it is always called
                    actualDict[featureXML['id']][key] = featureXML[key]
      
        
        self.assertDictEqual(expectedDict, actualDict)

    def test_ReaderException(self):
        self.assertRaises(IOError, parseFeatureXML.Reader, testFolder+'invalidXML.XML')

                              
    def test_getAllElements(self):
        expectedElementcount = 106
        
        featureXML = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
        allElements = featureXML.getAllElements()
        actualElementCount = 0
        for element in allElements:
           actualElementCount += 1
        
        self.assertEqual(expectedElementcount, actualElementCount)


    def test_getSimpleFeatureInfo(self):
        expectedFeatureCount = 4
        
        featureXML = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
        features = featureXML.getSimpleFeatureInfo()
        actualFeatureCount = 0
        for element in features:
            actualFeatureCount += 1
        
        self.assertEqual(expectedFeatureCount, actualFeatureCount)
    
    def test_getSimpleFeatureInfoException(self):
        featureXML = parseFeatureXML.Reader(testFolder+'invalidFeatureXML_noFeatures.featureXML')
        self.assertRaises(RuntimeError, lambda: list(featureXML.getSimpleFeatureInfo())) #lambda makes sure the whole loop is run


    def test_getAllFeatureInfo(self):
        expectedFeatureCount = 4
        
        featureXML = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
        features = featureXML.getAllFeatureInfo()
        actualFeatureCount = 0
        for element in features:
            actualFeatureCount += 1
        
        self.assertEqual(expectedFeatureCount, actualFeatureCount)
        
    def test_getAllFeatureInfoException(self): 
        featureXML = parseFeatureXML.Reader(testFolder+'invalidFeatureXML_noFeatures.featureXML')
        self.assertRaises(RuntimeError, lambda: list(featureXML.getAllFeatureInfo())) #lambda makes sure the whole loop is run

   
    def test_getAllNonFeatures(self):
        expectedNonFeatureCount = 4
        
        featureXML = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
        features = featureXML.getSimpleFeatureInfo()
        actualNonFeatureCount = 0
        for element in features:
            actualNonFeatureCount += 1
        
        self.assertEqual(expectedNonFeatureCount, actualNonFeatureCount)
    
    
    def test_getKeys(self):
        expectedKeys = set(['convexhull', 'charge', 'content', 'intensity', 'retention time', 'mz', 'overallquality', 'userParam', 'quality', 'id'])

        featureXML = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
        actualKeys =  featureXML.getKeys()
        
        self.assertSetEqual(expectedKeys, actualKeys)
    
    
    def test_getAllFeatureId(self):
        expectedIdList = ['f_130205234428175237334','f_13020522388175237334','f_8613715360396561740','f_43922326584371237334']

        
        featureXML = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
        acutalIdList = []
        for id in featureXML.getAllFeatureId():
            acutalIdList.append(id)
        
        self.assertListEqual(expectedIdList, acutalIdList)
    
    def test_getAllFeatureIdException(self):
        featureXML = parseFeatureXML.Reader(testFolder+'invalidFeatureXML_noFeatures.featureXML')
        self.assertRaises(RuntimeError, lambda: list(featureXML.getAllFeatureId())) #lambda makes sure the whole loop is run
   

    
def suite():
    suite = unittest.TestSuite()
    # adding the unit tests to the test suite
    suite.addTest(unittest.makeSuite(testParseFeatureXML))
    return suite

unittest.TextTestRunner(verbosity=1).run(suite())