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
Unit test of parseMascot.py
"""

# author: ndeklein
# date:10/02/2012
# summary: Unit testing functionality of the parseMascot.py script


import sys 
import os
# to be able to import unittest2 from a locally installed unittest2     * REMOVE WHEN SENDING TO OTHER USERS *
try:
    sys.path.append('/homes/ndeklein/python2.6/site-packages')
    sys.path.append('/homes/ndeklein/workspace/MS/Trunk/PyMS_dev/pyMS')
except:
    pass

# some magic to import from pyMS. dirname(dirname(__file__)) gets the two directories closer to the root.
# this is so that pyMS is added to the pythonpath and you can do import parseFeatureXML.py
# if this is made in a package from pyMS import parseFeatureXML should also work
dirname = os.path.dirname
sys.path.append(os.path.join(dirname(dirname(__file__))))
import unittest2 as unittest
import config
import parseMascot

import collections

configHandle =  config.ConfigHandle()
config = configHandle.getConfig()
testFolder = os.path.join(os.path.dirname(__file__), config.get('test','testfilefolder'))


class testParseMascot(unittest.TestCase):
    """
    A test class for the output module.
    """
    
    def test_Reader(self):
        expectedDict = {}
        actualDict = {}
        mascot = parseMascot.Reader(testFolder+'test_mascot.xml')   # make a Reader instance
    
    def test_getAllElements(self):
        expectedElementcount = 108
        
        mascot = parseMascot.Reader(testFolder+'test_mascot.xml')   # make a Reader instance
        allElements = mascot.getAllElements()
        actualElementCount = 0
        for element in allElements:
           actualElementCount += 1
        self.assertEqual(expectedElementcount, actualElementCount) 
    
    def test_getAssignedPeptidesMZandRTvalue(self):
        expectedResult = {'rt': '751.5624', 'protAccession': 'IPI00110850', 'mz': '462.240142822266'}

        mascot = parseMascot.Reader(testFolder+'test_mascot.xml')    # make a read instance
        for result in mascot.getAssignedPeptidesMZandRTvalue():
            actualResult = result
        
        self.assertDictEqual(expectedResult, actualResult) 
    

    def test_getAssignedPeptidesMZandRTvalue(self):
        expectedResult = {'mz': '335.222412109375','pep_calc_mr': '668.3534',  'pep_delta': '0.0769','pep_exp_mr': '668.4303','pep_exp_mz': '335.2224'\
                            ,'pep_exp_z': '2','pep_expect': '4e+02','pep_miss': '0','pep_num_match': None,'pep_scan_title': '335.222412109375_2270.0684'\
                            ,'pep_score': '12.72','pep_seq': 'FLDFK','pep_var_mod': None,'pep_var_mod_pos': None,'rt': '2270.0684'}

        mascot = parseMascot.Reader(testFolder+'test_mascot.xml')    # make a read instance
        for result in mascot.getUnassignedPeptidesMZandRTvalue():
            actualResult = result
        
        self.assertDictEqual(expectedResult, actualResult)   
    
def suite():
    suite = unittest.TestSuite()
    # adding the unit tests to the test suite
    suite.addTest(unittest.makeSuite(testParseMascot))
    return suite

unittest.TextTestRunner(verbosity=2).run(suite())
