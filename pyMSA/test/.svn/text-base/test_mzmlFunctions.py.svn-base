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
Unit test of mzmlFunctions.py
"""

# author: ndeklein
# date:10/02/2012
# summary: Unit testing functionality of the mzmlFunctions.py script


import sys 
import os
# to be able to import unittest2 from a locally installed unittest2     * REMOVE WHEN SENDING TO OTHER USERS *
try:
    sys.path.append('/homes/ndeklein/python2.6/site-packages')
except:
    pass# some magic to import from pyMS. dirname(dirname(__file__)) gets the two directories closer to the root.
# this is so that pyMS is added to the pythonpath and you can do import mzmlFunctions.py
# if this is made in a package from pyMS import mzmlFunctions should also work
dirname = os.path.dirname
sys.path.append(os.path.join(dirname(dirname(__file__))))
import unittest2 as unittest
import config
import mzmlFunctions
import pymzml


configHandle =  config.ConfigHandle()
config = configHandle.getConfig()
testFolder = config.get('test','testfilefolder')


class testMzmlFunctions_mzmlFile(unittest.TestCase):
    """
    A test class for the mzmlFunctions module.
    
    B{Got to improve the testfiles, the one I'm currently using, mzml_testFIle_withBinary.mzML, does not contain ms level 2
    spectra, so the expectedPrecursorKeys is always empty.}
    """
    
    def test_getPrecursorRtMz(self):
        expectedPrecursorRtMz_mzml = [{'mz': 337.33999999999997, 'rt': 85.166666666666671},{'mz': 421.76077270507812, 'rt': 0.82813999999999999},{'mz': 462.24014282226562, 'rt': 12.52604},{'mz': 335.222412109375, 'rt': 37.834473333333335}]
        expectedPrecursorRtMz_peaks = [{'rt': 9.5545000000000009, 'mz': 421.758026123047}, {'rt': 49.688400000000001, 'mz': 421.760772705078}]
                   
        msrun_mzml = pymzml.run.Reader(testFolder+'mzml_test_file_1.mzML')
        msrun_peaks = pymzml.run.Reader(testFolder+'peaksMzmlTestfile.peaks.mzML')
        actualPrecursorRtMz_mzml = mzmlFunctions.getPrecursorRtMz(msrun_mzml)
        actualPrecursorRtMz_peaks = mzmlFunctions.getPrecursorRtMz(msrun_peaks)
        
        self.assertEqual(expectedPrecursorRtMz_mzml, actualPrecursorRtMz_mzml)
        self.assertEqual(expectedPrecursorRtMz_peaks, actualPrecursorRtMz_peaks)
    
    def test_getPrecursorRtMzException(self):
        self.assertRaises(TypeError, mzmlFunctions.getPrecursorRtMz, 'wrong type instance <str>')
        
        msrun = pymzml.run.Reader(testFolder+'invalidmzmlTestFile_noMSprecursor.mzML') # there are no ms level 2 spectra in this file
        self.assertRaises(RuntimeError, mzmlFunctions.getPrecursorRtMz, msrun)
    
    def test_getKeys_default(self):    
        # test getKeys with default, so no excluded or included keys
        expectedSpectrumKeys = set(['no compression', 'total ion current', 'scan time', 'filter string', 'id', 'profile mass spectrum',
                                     '64-bit float', 'defaultArrayLength', 'm/z array', 'ms level', 'intensity array',
                                     'BinaryArrayOrder', '32-bit float', 'total ion current chromatogram', 'time array'])
        expectedPrecursorKeys = set([])
       
        msrun = pymzml.run.Reader(testFolder+'mzml_testFIle_withBinary.mzML')
        actualSpectrumKeys, actualPrecursorKeys, spectrumList = mzmlFunctions.getKeys(msrun)

        self.assertSetEqual(expectedSpectrumKeys, actualSpectrumKeys)
        self.assertSetEqual(expectedPrecursorKeys, actualPrecursorKeys)
        
        
    def test_getKeys_exclusive(self):
        # test getKeys with some keys excluded
        expectedSpectrumKeys = set(['total ion current chromatogram', 'time array', '32-bit float', 'total ion current chromatogram', 'no compression', 'total ion current'])
        expectedPrecursorKeys = set([])

        
        msrun = pymzml.run.Reader(testFolder+'mzml_testFIle_withBinary.mzML')
        actualSpectrumKeys, actualPrecursorKeys, spectrumList = mzmlFunctions.getKeys(msrun, excludeList = ['scan time', 'filter string', 'PY:0000000', 'precursors', 'id', 'profile mass spectrum','collision-induced dissociation', '64-bit float', 'defaultArrayLength', 'm/z array', 'charge state', 'None', 'ms level', 'intensity array', 'BinaryArrayOrder', 'encodedData', 'mz'])
        
        self.assertSetEqual(expectedSpectrumKeys, actualSpectrumKeys)
        self.assertSetEqual(expectedPrecursorKeys, actualPrecursorKeys)
    
    
    def test_getKeys_inclusive(self):
        # test getKeys with some keys excluded and some keys includes
        expectedSpectrumKeys = set(['no compression', 'total ion current','time array', '32-bit float', 'total ion current chromatogram'])
        expectedPrecursorKeys = set([])

        
        msrun = pymzml.run.Reader(testFolder+'mzml_testFIle_withBinary.mzML')
        actualSpectrumKeys, actualPrecursorKeys, spectrumList = mzmlFunctions.getKeys(msrun, excludeList = ['charge','scan time', 'filter string', 'PY:0000000', 'precursors', 'id', 'profile mass spectrum', 'charge','collision-induced dissociation', '64-bit float', 'defaultArrayLength', 'm/z array', 'charge state', 'None', 'ms level', 'intensity array', 'BinaryArrayOrder', 'encodedData', 'charge'])
        
        self.assertSetEqual(expectedSpectrumKeys, actualSpectrumKeys)
        self.assertSetEqual(expectedPrecursorKeys, actualPrecursorKeys)

    
    def test_getKeysException(self):
        msrun = pymzml.run.Reader(testFolder+'mzml_test_file_1.mzML')
        self.assertRaises(TypeError, mzmlFunctions.getKeys, msrun,excludeList = {'a different fileformat':'not a list'})
        self.assertRaises(TypeError, mzmlFunctions.getKeys, msrun,includeList = {'a different fileformat':'not a list'})
        self.assertRaises(TypeError, mzmlFunctions.getKeys, msrun,includeList = 'a different fileformat', excludeList = 'not a list')

    
    def test_getChargeStateAbundance(self):
        expectedDict = {2: 4}
        
        msrun = pymzml.run.Reader(testFolder+'mzml_test_file_1.mzML')       
        actualDict = mzmlFunctions.getChargeStateAbundance(msrun)
  
        self.assertDictEqual(expectedDict, actualDict)
    
    def test_getTotalMScount(self):
        expectedDict = {'MS':4, 'MS/MS':4}
        
        msrun = pymzml.run.Reader(testFolder+'mzml_test_file_1.mzML')       
        actualDict = mzmlFunctions.getTotalMScount(msrun)
  
        self.assertDictEqual(expectedDict, actualDict)
    
    def test_getIntensityFromMZwindow(self):
        #mzmlInstance = pymzml.run.Reader(testFolder+'mzml_testFIle_withBinary.mzML')
        mzmlInstance = pymzml.run.Reader('/homes/dmamartin/Documents/PROTEOMICS/Cantrell/openMS/JG-C1-1A.mzML')
        intensityFromSpectra = mzmlFunctions.IntensityFromSpectra(mzmlInstance)
        actualRetentionList, actualIntensityList = intensityFromSpectra.getIntensityFromMZwindow(399, 400)
        
    def test_getIntensityFromMZwindowException(self):
        mzmlInstance = pymzml.run.Reader(testFolder+'mzml_testFIle_withBinary.mzML')
        intensityFromSpectra = mzmlFunctions.IntensityFromSpectra(mzmlInstance)
        intensityFromSpectra = mzmlFunctions.IntensityFromSpectra(mzmlInstance)
        self.assertRaises(TypeError, mzmlFunctions.IntensityFromSpectra, 'not a pymzml.run.Reader() instance')
        self.assertRaises(TypeError, intensityFromSpectra.getIntensityFromMZwindow, 'not an int', 4)
        self.assertRaises(TypeError, intensityFromSpectra.getIntensityFromMZwindow, 1200, 'not an int')


def suite():
    suite = unittest.TestSuite()
    # adding the unit tests to the test suite
    suite.addTest(unittest.makeSuite(testMzmlFunctions_mzmlFile))
    return suite



unittest.TextTestRunner(verbosity=1).run(suite())