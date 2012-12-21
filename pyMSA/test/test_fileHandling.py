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
Unit test of fileHandling.py
"""

# author: ndeklein
# date:10/02/2012
# summary: Unit testing functionality of the fileHandling.py script


import sys 
import os
# to be able to import unittest2 from a locally installed unittest2     * REMOVE WHEN SENDING TO OTHER USERS *
try:
    sys.path.append('/homes/ndeklein/python2.6/site-packages')
except:
    pass# some magic to import from pyMS. dirname(dirname(__file__)) gets the two directories closer to the root.
# this is so that pyMS is added to the pythonpath and you can do import fileHandling.py
# if this is made in a package from pyMS import fileHandling should also work
dirname = os.path.dirname
sys.path.append(os.path.join(dirname(dirname(__file__))))
import unittest2 as unittest
import config
import parseFeatureXML
import fileHandling

configHandle =  config.ConfigHandle()
config = configHandle.getConfig()
testFolder = config.get('test','testfilefolder')


class testFileHandling(unittest.TestCase):
    """
    A test class for the fileHandling module.
    """
    def test_fileHandleException(self):
        # the genereal IOError when a file does not exist
        self.assertRaises(IOError, fileHandling.FileHandle, testFolder+'fakefile.txt')
        
        
    def test_isXML(self):
        validXmlFile = testFolder+'validXML.XML'
        fileHandler = fileHandling.FileHandle(validXmlFile)
        # if no error is given test passes
        self.assertEqual(fileHandler.isXML(), None)
        

    def test_isXML_invalidException(self):
        invalidXmlFile = testFolder+'/invalidXML.XML'
        fileHandler = fileHandling.FileHandle(invalidXmlFile)
        # test if isXML gives the right error (IOError) when called with an invalid XML file 
        self.assertRaises(IOError, fileHandler.isXML)

    
    def test_isFeatureXML(self):
        validFeatureXML = testFolder+'featurexmlTestFile_1.featureXML'
        # if no error is given test passes
        fileHandler = fileHandling.FileHandle(validFeatureXML)
        self.assertEqual(fileHandler.isFeatureXML(), None)
    
    def test_isFeatureXML_invalidException(self):
        invalidFeatureXML = testFolder+'invalidFeatureXML_noheader.featureXML'
        fileHandler = fileHandling.FileHandle(invalidFeatureXML)
        # test if isFeatureXML gives the right error (IOError) when called with an invalid XML file 
        self.assertRaises(IOError, fileHandler.isFeatureXML)
        
    def test_isMzML(self):
        validMzML = testFolder+'mzml_test_file_1.mzML'
        fileHandler = fileHandling.FileHandle(validMzML)
        fileHandler.isMzML()
        self.assertEqual(fileHandler.isMzML(), None)
    
    def test_isMzMLException(self):
        invalidMzML = testFolder+'featurexmlTestFile_1.featureXML'
        fileHandler = fileHandling.FileHandle(invalidMzML)
        self.assertRaises(IOError, fileHandler.isMzML)
    
    def test_isMascot(self):
        validMascot = testFolder+'MASCOT_scan_in_title.xml'
        fileHandler = fileHandling.FileHandle(validMascot)
        fileHandler.isMascot()
        # no error means it passed
    
    def test_isMascotException(self):
        invalidMascot = testFolder+'featurexmlTestFile_1.featureXML'
        fileHandler = fileHandling.FileHandle(invalidMascot)
        self.assertRaises(IOError, fileHandler.isMascot)
    
    def test_getFile(self):
        fileHandle = fileHandling.FileHandle(testFolder+'featurexmlTestFile_1.featureXML')
        self.assertEqual(fileHandle.getFile(), testFolder+'featurexmlTestFile_1.featureXML')
    
    
        
def suite():
    suite = unittest.TestSuite()
    # adding the unit tests to the test suite
    suite.addTest(unittest.makeSuite(testFileHandling))
    return suite

unittest.TextTestRunner(verbosity=1).run(suite())