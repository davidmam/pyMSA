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
Unit test of baseFunctions.py
"""

# author: ndeklein
# date:10/02/2012
# summary: Unit testing functionality of the baseFunctions.py script


import sys 
import os
# to be able to import unittest2 from a locally installed unittest2     * REMOVE WHEN SENDING TO OTHER USERS *
try:
    sys.path.append('/homes/ndeklein/python2.6/site-packages')
except:
    pass
# some magic to import from pyMS. dirname(dirname(__file__)) gets the two directories closer to the root.
# this is so that pyMS is added to the pythonpath and you can do import baseFunctions.py
# if this is made in a package from pyMS import baseFunctions should also work
dirname = os.path.dirname
sys.path.append(os.path.join(dirname(dirname(__file__))))
import unittest2 as unittest
import elementFunctions
import config
from xml.etree import cElementTree
configHandle =  config.ConfigHandle()
config = configHandle.getConfig()
testFolder = os.path.join(os.path.dirname(__file__), config.get('test','testfilefolder'))

class testElementFunctions(unittest.TestCase):
        
    def test_getItems(self):
        expectedItems = {'{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation': 'http://open-ms.sourceforge.net/schemas/FeatureXML_1_4.xsd', 'version': '1.4', 'id': 'fm_2007447552192692304'}
        # use the celementtree iterparse function to get one element
        
        elementFile = open(testFolder+'featurexmlTestFile_1.featureXML')
        for event, element in cElementTree.iterparse(elementFile):      # looping through the tree
            itemsDict = elementFunctions.getItems(element)                 # getting the items of all elements in the tree
        self.assertDictContainsSubset(expectedItems, itemsDict)                      # assert that the itemsDict dictionary contains the subset of the expectedItems dict

    def test_getItemsException(self):
        notElement = 'not an element'
        self.assertRaises(TypeError, elementFunctions.getItems, notElement)


    def test_getAllNestedItems(self):
        expectedItems = {'fullName': 'Proteomics Standards Initiative Mass Spectrometry Ontology', 'id': '', 'URI': 'http://psidev.cvs.sourceforge.net/*checkout*/psidev/psi/psi-ms/mzML/controlledVocabulary/psi-ms.obo','fullName': 'Proteomics Standards Initiative Mass Spectrometry Ontology','id': 'MS'}
        
        # dict to hold everythin that getAllNestedItems returns
        actualItems = {}
        elementFile = open(testFolder+'peaksMzmlTestfile.peaks.mzML')
        for event, element in cElementTree.iterparse(elementFile):
            items = elementFunctions.getAllNestedItems(element)
            for item in items:
                actualItems.update(item)
            # only doing one to test, break
            break
        
        self.assertDictEqual(expectedItems, actualItems)
        
    def test_getAllNestedElementInformation(self):
        expectedResultPeaks = {'fullName': 'Proteomics Standards Initiative Mass Spectrometry Ontology', 'id': 'MS', 'tagName': '{http://psi.hupo.org/ms/mzml}cv', 
                               'URI': 'http://psidev.cvs.sourceforge.net/*checkout*/psidev/psi/psi-ms/mzML/controlledVocabulary/psi-ms.obo'}
        expectedResultMzml = {'fullName': 'Proteomics Standards Initiative Mass Spectrometry Ontology', 'id': 'MS', 'tagName': '{http://psi.hupo.org/ms/mzml}cv', 
                              'URI': 'http://psidev.cvs.sourceforge.net/*checkout*/psidev/psi/psi-ms/mzML/controlledVocabulary/psi-ms.obo', 'version':'2.26.0'}
        expectedResultFeatureXML = {'name': 'FeatureFinder', 'tagName': 'software', 'version': '1.8.0'}

        actualResultPeaks = {}
        elementFile = open(testFolder+'peaksMzmlTestfile.peaks.mzML')
        for event, element in cElementTree.iterparse(elementFile):
            actualResultPeaks = elementFunctions.getAllNestedElementInformation(element)
            # only doing one to test, break
            break
        
        actualResultMzml = {}
        elementFile = open(testFolder+'mzml_test_file_1.mzML')
        for event, element in cElementTree.iterparse(elementFile):
            actualResultMzml = elementFunctions.getAllNestedElementInformation(element)
            # only doing one to test, break
            break

        actualResultFeatureXML = {}
        elementFile = open(testFolder+'featurexmlTestFile_1.featureXML')
        for event, element in cElementTree.iterparse(elementFile):
            actualResultFeatureXML = elementFunctions.getAllNestedElementInformation(element)
            # only doing one to test, break
            break
            
        
        self.assertDictEqual(expectedResultPeaks, actualResultPeaks)
        self.assertDictEqual(expectedResultMzml, actualResultMzml)
        self.assertDictEqual(expectedResultFeatureXML, actualResultFeatureXML)

def suite():
    suite = unittest.TestSuite()
    # adding the unit tests to the test suite
    suite.addTest(unittest.makeSuite(testElementFunctions))
    return suite

unittest.TextTestRunner(verbosity=2).run(suite())