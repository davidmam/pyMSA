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
Unit test of getWindow.py
"""

# author: ndeklein
# date:10/02/2012
# summary: Unit testing functionality of the getWindow.py script


import sys 
import os
# to be able to import unittest2 from a locally installed unittest2	 * REMOVE WHEN SENDING TO OTHER USERS *
try:
	sys.path.append('/homes/ndeklein/python2.6/site-packages')
except:
	pass

# some magic to import from pyMS. dirname(dirname(__file__)) gets the two directories closer to the root.
# this is so that pyMS is added to the pythonpath and you can do import featureFunctions.py
# if this is made in a package from pyMS import featureFunctions should also work
dirname = os.path.dirname
sys.path.append(os.path.join(dirname(dirname(__file__))))
import unittest2 as unittest
import config
import parseFeatureXML
import parsePeaksMzML
import getWindow
import pymzml

configHandle =  config.ConfigHandle()
config = configHandle.getConfig()
testFolder = config.get('test','testfilefolder')


class testGetWindow(unittest.TestCase):
	"""
	A test class for the getWindow module.
	
	"""

	def test_getFeatures_mzWindow(self):
		featureXML = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
		featureLocation = getWindow.FeatureLocation(featureXML)
		featureList = []
		for feature in featureLocation.getFeatures_mzWindow(300,500):
			featureList.append(feature)
			
		self.assertIs(4, len(featureList))
		
	def test_getFeatures_mzWindowException(self):
		featureXML = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
		featureLocation = getWindow.FeatureLocation(featureXML)
		self.assertRaises(TypeError, lambda: featureLocation.getFeatures_mzWindow, 'not an int', 1)
		self.assertRaises(TypeError, lambda: featureLocation.getFeatures_mzWindow , 1, 'not an int')
		

	def test_getFeatures_rtWindow(self):
		featureXML = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
		featureLocation = getWindow.FeatureLocation(featureXML)
		featureList = []
		for feature in featureLocation.getFeatures_rtWindow(4000,5000):
			featureList.append(feature)
			
		self.assertIs(0, len(featureList))
		
	def test_getFeatures_rtWindowException(self):
		featureXML = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
		featureLocation = getWindow.FeatureLocation(featureXML)
		self.assertRaises(TypeError, lambda: featureLocation.getFeatures_rtWindow, 'not an int', 1)
		self.assertRaises(TypeError, lambda: featureLocation.getFeatures_rtWindow , 1, 'not an int')
	
	
		
	def test_getPeaks_mzWindow(self):
		peaks = parsePeaksMzML.Reader(testFolder+'peaksMzmlTestfile.peaks.mzML')
		peakLocation = getWindow.PeakLocation(peaks)
		peakList = []
		for peak in peakLocation.getPeaks_mzWindow(350,500):
			peakList.append(peak)
		
		self.assertIs(3, len(peakList))
	
		
	def test_getPeaks_mzWindowException(self):
		peaks = parsePeaksMzML.Reader(testFolder+'peaksMzmlTestfile.peaks.mzML')
		peakLocation = getWindow.PeakLocation(peaks)
		self.assertRaises(TypeError, lambda: peakLocation.getPeaks_mzWindow, 'not an int', 1)
		self.assertRaises(TypeError, lambda: peakLocation.getPeaks_mzWindow , 1, 'not an int')
		

	def test_getPeaks_rtWindow(self):
		peaks = parsePeaksMzML.Reader(testFolder+'peaksMzmlTestfile.peaks.mzML')
		peakLocation = getWindow.PeakLocation(peaks)
		peakList = []
		for peak in peakLocation.getPeaks_rtWindow(500,3000):
			peakList.append(peak) 
		
		self.assertIs(4, len(peakList))
		
	def test_getPeaks_rtWindowException(self):
		peaks = parsePeaksMzML.Reader(testFolder+'peaksMzmlTestfile.peaks.mzML')
		peakLocation = getWindow.PeakLocation(peaks)
		self.assertRaises(TypeError, lambda: peakLocation.getPeaks_rtWindow, 'not an int', 1)
		self.assertRaises(TypeError, lambda: peakLocation.getPeaks_rtWindow , 1, 'not an int')
	
	def test_getSpectra_mzWindow(self):
		mzmlInstance = pymzml.run.Reader(testFolder+'mzml_testFIle_withBinary.mzML')
		spectraLocation = getWindow.SpectraLocation(mzmlInstance)
		spectraList = []
		for spectrum in spectraLocation.getSpectra_mzWindow(400, 500):
			spectraList.append(spectrum)
		
		self.assertEqual(12998, len(spectraList))
		
	def test_getSpectra_mzWindowException(self):
		mzmlInstance = pymzml.run.Reader(testFolder+'mzml_testFIle_withBinary.mzML')
		spectraLocation = getWindow.SpectraLocation(mzmlInstance)
		self.assertRaises(TypeError, lambda: spectraLocation.getSpectra_mzWindow, 'not an int', 1)
		self.assertRaises(TypeError, lambda: spectraLocation.getSpectra_mzWindow , 1, 'not an int')		

	def test_getSpectra_rtWindow(self):
		mzmlInstance = pymzml.run.Reader(testFolder+'mzml_test_file_1.mzML')
		spectraLocation = getWindow.SpectraLocation(mzmlInstance)
		spectraList = []
		for spectrum in spectraLocation.getSpectra_rtWindow(300, 500):
			spectraList.append(spectrum)
		
		self.assertIs(1, len(spectraList))
		
	def test_getSpectra_rtWindowException(self):
		mzmlInstance = pymzml.run.Reader(testFolder+'mzml_test_file_1.mzML')
		spectraLocation = getWindow.SpectraLocation(mzmlInstance)
		self.assertRaises(TypeError, lambda: spectraLocation.getSpectra_rtWindow, 'not an int', 1)
		self.assertRaises(TypeError, lambda: spectraLocation.getSpectra_rtWindow , 1, 'not an int')		


def suite():
	suite = unittest.TestSuite()
	# adding the unit tests to the test suite
	suite.addTest(unittest.makeSuite(testGetWindow))
	return suite
	
unittest.TextTestRunner(verbosity=1).run(suite())