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
Unit test of featureFunctions.py
"""

# author: ndeklein
# date:10/02/2012
# summary: Unit testing functionality of the featureFunctions.py script


import sys 
import os
# to be able to import unittest2 from a locally installed unittest2	 * REMOVE WHEN SENDING TO OTHER USERS *
try:
	sys.path.append('/homes/ndeklein/python2.6/site-packages')
except:
	pass# some magic to import from pyMS. dirname(dirname(__file__)) gets the two directories closer to the root.
# this is so that pyMS is added to the pythonpath and you can do import featureFunctions.py
# if this is made in a package from pyMS import featureFunctions should also work
dirname = os.path.dirname
sys.path.append(os.path.join(dirname(dirname(__file__))))
import unittest2 as unittest
import config
import parseFeatureXML
import featureFunctions

configHandle =  config.ConfigHandle()
config = configHandle.getConfig()
testFolder = config.get('test','testfilefolder')


class testFeatureFunctions(unittest.TestCase):
	"""
	A test class for the featureFunctions module.
	
	B{<TODO>:}
	
		- write test for a featureXML made by FeatureFinder version 1.7.0 (now done only with a version 1.8.0) 
	"""

	def test_getFeatureConvexhullCoordinates(self):
		expectedFeatureConvexhull = [[{'mzMax': '338.251376135343', 'rtMin': '7045.7642', 'rtMax': '7053.4848', 'mzMin': '336.124751115092'}], [{'mzMax': '338.251376135343', 'rtMin': '5105.9217', 'rtMax': '5111.6874', 'mzMin': '336.124751115092'}], [{'mzMax': '430.197574989105', 'rtMin': '4001.7973', 'rtMax': '4017.7105', 'mzMin': '428.070943557216'}], [{'mzMax': '339.251376135343', 'rtMin': '5107.9217', 'rtMax': '5112.6874', 'mzMin': '337.124751115092'}]]

		featureXML = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
		actualFeatureConvexhull = []
		for feature in featureXML.getSimpleFeatureInfo():
			actualFeatureConvexhull.append(featureFunctions.getFeatureConvexhullCoordinates(feature).values()) # only looking at the values because the features are stored at locations which differ between calls, so don't know what to expect
			self.assertEqual(str(type(featureFunctions.getFeatureConvexhullCoordinates(feature).keys()[0])), '<type \'Element\'>') # I don't know where ther class Element comes from so I convert the type to string and compare the strings
		
		
		self.assertListEqual(expectedFeatureConvexhull, actualFeatureConvexhull)

	def test_getFeatureConvexhullCoordinatesException(self):
		self.assertRaises(TypeError, featureFunctions.getFeatureConvexhullCoordinates, 'not element type') # input is a string instead of type element, should give type error
		featureXML = parseFeatureXML.Reader(testFolder+'invalidFeatureXML_noconvexhull.featureXML')
		for feature in featureXML.getSimpleFeatureInfo():
			self.assertRaises(IOError, featureFunctions.getFeatureConvexhullCoordinates, feature) # this should give an IOError because the file given to parseFeatureXML.Reader is not a valid featureXML File (the features don't have a convexhull

	def test_getFeatureOverlap(self):
		expectedOverlap = 43
		
		featureXML = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')   # make a reader instance
		featureDict = {}	
		for feature in featureXML.getSimpleFeatureInfo():   # get all the features in featureXML and loop through them. Because the for loop gets the convexhull coordinates one at a time, the convexhulls first have to be put in one big dictionary before they can be given to getOverlap
			featureDict.update(featureFunctions.getFeatureConvexhullCoordinates(feature))		# getFeatureConvexhullCoordinates returns a dictionary, so featureDict can be updated with .update()
		actualOverlap = featureFunctions.getOverlap(featureDict)
		
		self.assertTrue(expectedOverlap, actualOverlap)

def suite():
	suite = unittest.TestSuite()
	# adding the unit tests to the test suite
	suite.addTest(unittest.makeSuite(testFeatureFunctions))
	return suite

	
unittest.TextTestRunner(verbosity=1).run(suite())