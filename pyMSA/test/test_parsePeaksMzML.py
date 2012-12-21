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
Unit test of parsePeaksMzML.py
"""

# author: ndeklein
# date:10/02/2012
# summary: Unit testing functionality of the parsePeaksMzML.py script


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
import parsePeaksMzML

import collections

configHandle =  config.ConfigHandle()
config = configHandle.getConfig()
testFolder = config.get('test','testfilefolder')


class testParsePeaksMzML(unittest.TestCase):
    """
    A test class for the output module.
    """
    
    def test_Reader(self):
        expectedDict = {'no compression': 'no compression', 'total ion current': '1944280.875', '32-bit float': '32-bit float',
                        '64-bit float': '64-bit float','[thermo trailer extra]monoisotopic m/z:': '421.760772705078','activation energy': '0',
                        'base peak intensity': '204693.875','base peak m/z': '348.990112304688','centroid spectrum': 'centroid spectrum',
                        'charge state': '2','collision energy': '35','collision-induced dissociation': 'collision-induced dissociation',
                        'filter string': 'FTMS + p NSI Full ms [335.00-1800.00]','highest observed m/z': '1807.22747568909', 
                        'intensity array': 'intensity array','isolation window lower offset': '1', 'isolation window target m/z': '421.760772705078',
                        'isolation window upper offset': '1', 'lowest observed m/z': '334.999113612625','m/z array': 'm/z array','mass spectrum': 'mass spectrum',
                        'ms level': '1','no combination': 'no combination','no compression': 'no compression','peak intensity': '567.059326171875',
                        'positive scan': 'positive scan','preset scan configuration': '1', 'scan start time': '49.9378','scan window lower limit': '335',
                        'scan window upper limit': '1800','scan_id': '52','selected ion m/z': '421.760772705078','total ion current': '1944280.875'}
        actualDict = {}
        peaksMzML = parsePeaksMzML.Reader(testFolder+'peaksMzmlTestfile.peaks.mzML')   # make a Reader instance
        spectra = peaksMzML.getSimpleSpectraInfo()                    # get all the spectra of the Reader instance
        for spectrum in spectra:                            # loop through all the spectra
            for keys in peaksMzML.getKeys():  # get all the keys
                actualDict[keys] = peaksMzML[keys]

        
        self.assertDictEqual(expectedDict, actualDict)

    def test_ReaderException(self):
        self.assertRaises(IOError, parsePeaksMzML.Reader, testFolder+'invalidXML.XML')
  
    
    def test_getAllElements(self):
        expectedElementcount = 253
        
        peaksMzML = parsePeaksMzML.Reader(testFolder+'peaksMzmlTestfile.peaks.mzML')   # make a Reader instance
        allElements = peaksMzML.getAllElements()
        actualElementCount = 0
        for element in allElements:
           actualElementCount += 1
        
        self.assertEqual(expectedElementcount, actualElementCount) 
        
    
    def test_getSpectra(self):
        expectedMaxId = 52 
        
        peaksMzML = parsePeaksMzML.Reader(testFolder+'peaksMzmlTestfile.peaks.mzML')   # make a Reader instance
        spectra = peaksMzML.getSimpleSpectraInfo()
        for spectrum in spectra:
            actualMaxId = int(peaksMzML['scan_id']) # this will hold the last value of the loop, so the max value
        
        self.assertEqual(expectedMaxId, actualMaxId)
              
    def test_getKeys(self):
        expectedKeySet = set(['no compression','total ion current','filter string','scan_id','isolation window upper offset', 
                              'collision-induced dissociation','scan start time','64-bit float','intensity array','isolation window lower offset',
                              'positive scan','peak intensity','no combination','centroid spectrum','base peak m/z','m/z array','ms level',
                              'selected ion m/z','scan window lower limit','highest observed m/z','preset scan configuration','base peak intensity',
                              '32-bit float','mass spectrum','[thermo trailer extra]monoisotopic m/z:','scan window upper limit','isolation window target m/z',
                              'collision energy','lowest observed m/z','charge state','activation energy'])
        
        peaksMzML = parsePeaksMzML.Reader(testFolder+'peaksMzmlTestfile.peaks.mzML')   # make a Reader instance
        spectra = peaksMzML.getSimpleSpectraInfo()
        actualKeySet = set([])
        for spectrum in spectra:
            for keys in peaksMzML.getKeys():
                actualKeySet.add(keys)
        
        self.assertSetEqual(expectedKeySet, actualKeySet)        
        
    def test_getitems(self):
        peaksMzML = parsePeaksMzML.Reader(testFolder+'peaksMzmlTestfile.peaks.mzML')   # make a Reader instance
        spectra = peaksMzML.getSimpleSpectraInfo()
        for spectrum in spectra:
            for key in peaksMzML.getKeys():
                # if this does not give any errors it means it works.
                peaksMzML[key]
    

    
def suite():
    suite = unittest.TestSuite()
    # adding the unit tests to the test suite
    suite.addTest(unittest.makeSuite(testParsePeaksMzML))
    return suite

unittest.TextTestRunner(verbosity=1).run(suite())