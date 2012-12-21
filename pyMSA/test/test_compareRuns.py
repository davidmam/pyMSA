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
Unit test of compareRuns.py
"""

# author: ndeklein
# date:10/02/2012
# summary: Unit testing functionality of the compareRuns.py script


import sys 
import os
# to be able to import unittest2 from a locally installed unittest2 and pymzml    * REMOVE WHEN SENDING TO OTHER USERS *
sys.path.append('/homes/ndeklein/python2.6/site-packages')
# some magic to import from pyMS. dirname(dirname(__file__)) gets the two directories closer to the root.
# this is so that pyMS is added to the pythonpath and you can do import config.py
# if this is made in a package from pyMS import config should also work
dirname = os.path.dirname
sys.path.append(os.path.join(dirname(dirname(__file__))))
import unittest2 as unittest
import compareRuns
import config
configHandle =  config.ConfigHandle()
config = configHandle.getConfig()
testFolder = config.get('test','testfilefolder')
import pymzml

class testCompareRuns(unittest.TestCase):
    """
    A test class for the compareRuns module.
    """

    def test_CompareRuns(self):
        # no error means it passes
        msrun1 = pymzml.run.Reader(testFolder+'mzml_test_file_1.mzML')
        msrun2 = pymzml.run.Reader(testFolder+'mzml_test_file_2.mzML')
        msrun3 = pymzml.run.Reader(testFolder+'mzml_test_file_3.mzML')
        compare = compareRuns.CompareRuns(msrun1, msrun2, msrun3)
        
    
    def test_CompareRunsException(self):
        # CompareRuns expects at least 2 arguments
        self.assertRaises(TypeError, compareRuns.CompareRuns)
        self.assertRaises(TypeError, compareRuns.CompareRuns, 'one arguent')
        
        # CompareRuns expects a pymzml.run.Reader type
        self.assertRaises(TypeError, compareRuns.CompareRuns, 'not pymzml.run.Reader', 'this neither')
        
    def test_compare_mzML(self):
        msrun1 = pymzml.run.Reader(testFolder+'example_aligned_file_1.aligned.mzML')
        msrun2 = pymzml.run.Reader(testFolder+'example_aligned_file_2.aligned.mzML')
        compare = compareRuns.CompareRuns(msrun1, msrun2)
        compare.compare_mzML()
        
def suite():
    suite = unittest.TestSuite()
    # adding the unit tests to the test suite
    suite.addTest(unittest.makeSuite(testCompareRuns))
    return suite

unittest.TextTestRunner(verbosity=1).run(suite())