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
testFolder = config.get('test','testfilefolder')


class testParseMascot(unittest.TestCase):
    """
    A test class for the output module.
    """
    
    def test_Reader(self):
        expectedDict = {}
        actualDict = {}
        mascot = parseMascot.Reader(testFolder+'MASCOT_mzrt_in_title.xml')   # make a Reader instance no error is pass
    
    def test_getAllElements(self):
        expectedElementcount = 108
        
        mascot = parseMascot.Reader(testFolder+'MASCOT_mzrt_in_title.xml')   # make a Reader instance
        allElements = mascot.getAllElements()
        actualElementCount = 0
        for element in allElements:
           actualElementCount += 1
        self.assertEqual(expectedElementcount, actualElementCount) 

    def test_setRegularExpression(self):
        mascot = parseMascot.Reader(testFolder+'MASCOT_mzrt_in_title.xml')   # make a Reader instance
        mascot.setScanRE('<*?A*.')
        mascot.setFileRE('<*?A*.')
        mascot.setRtRE('<*?A*.')
        mascot.setMzRE('<*?A*.')
        self.assertEqual('<*?A*.', mascot.scan_re) 
        self.assertEqual('<*?A*.', mascot.file_re) 
        self.assertEqual('<*?A*.', mascot.mz_re) 
        self.assertEqual('<*?A*.', mascot.rt_re) 

    def test_setRegularExpressionException(self):
        mascot = parseMascot.Reader(testFolder+'MASCOT_mzrt_in_title.xml')   # make a Reader instance
        self.assertRaises(TypeError,mascot.setScanRE,1)
        self.assertRaises(TypeError,mascot.setFileRE,1)
        self.assertRaises(TypeError,mascot.setRtRE,1)
        self.assertRaises(TypeError,mascot.setMzRE,1)


    def test_getAssignedPeptidesMZandRTvalue(self):
        mzrtExpected = {'pep_exp_mr': '922.4657', 'pep_scan_title': '462.240142822266_751.5624', 'pep_delta': '-0.9844', 'pep_exp_mz': '462.2401',
                        'protAccession': 'IPI00110850', 'pep_calc_mr': '923.4501', 'pep_var_mod': 'Label:13C(6)15N(2) (K); Label:13C(6)15N(4) (R)',
                        'prot_matches_sig': '18', 'rt': '751.5624', 'pep_exp_z': '2', 'scannumber': None, 'pep_miss': '1', 
                        'pep_var_mod_pos': '0.0000065.0', 'fileroot': None, 'prot_sequences_sig': '5', 'pep_score': '20.31', 'prot_score': '767', 
                        'prot_sequences': '11', 'pep_res_after': 'D', 'prot_matches': '101', 'pep_res_before': 'K', 'pep_num_match': None, 
                        'pep_seq': 'CDVDIRK', 'prot_mass': '42058', 'prot_desc': 'SWISS-PROT:P60710|TREMBL:B2RRX1;Q3TIJ9;Q3U5R4;Q3UA89;Q3UAA9;Q3UAF6;Q3UAF7;Q3UBP6;Q3UGS0;Q61276|ENSEMBL:ENSMUSP00000031564|REFSEQ:NP_031419 Tax_Id=10090 Gene_Symbol=Actb Actin, cytoplasmic 1',
                        'pep_expect': '75', 'mz': '462.240142822266'}

        scanExpected = [{'pep_exp_mr': '987.4417', 'pep_scan_title': '947: Scan 51 (rt=30.6055) [\\\\wzw.tum.de\\ipag\\projects\\Phosphoscoring\\Manuscript\\Data\\Orbitrap_raw\\MSA_raw\\ppeptidemix3_MSA_Orbi.RAW]', 
                         'pep_delta': '-0.0009', 'pep_exp_mz': '494.7281', 'protAccession': 'IPI00166845', 'pep_calc_mr': '987.4426', 'pep_var_mod': 'Acetyl (N-term); Phospho (ST)', 
                         'prot_matches_sig': '39', 'rt': None, 'pep_exp_z': '2', 'scannumber': '51', 'pep_miss': '0', 'pep_var_mod_pos': '1.00000300.0', 'fileroot': None,'prot_sequences_sig': '2', 
                         'pep_score': '7.48', 'prot_score': '1678', 'prot_sequences': '3', 'pep_res_after': 'D', 'prot_matches': '65', 'pep_res_before': 'K', 'pep_num_match': None, 'pep_seq': 'GAYSLSIR', 
                         'prot_mass': '54827', 'prot_desc': 'Tax_Id=9606 Gene_Symbol=FYN Isoform 3 of Tyrosine-protein kinase Fyn', 'pep_expect': '14', 'mz': None},
                        {'pep_exp_mr': '987.4425', 'pep_scan_title': '747: Scan 1840 (rt=27.3349) [\\\\wzw.tum.de\\ipag\\projects\\Phosphoscoring\\Manuscript\\Data\\Orbitrap_raw\\MSA_raw\\ppeptidemix3_MSA_Orbi.RAW]', 
                         'pep_delta': '-0.0002', 'pep_exp_mz': '494.7285', 'protAccession': 'IPI00166845', 'pep_calc_mr': '987.4426', 'pep_var_mod': 'Acetyl (N-term); Phospho (ST)', 
                         'prot_matches_sig': '39', 'rt': None, 'pep_exp_z': '2', 'scannumber': '1840', 'pep_miss': '0', 'pep_var_mod_pos': '1.00000300.0', 'fileroot': None, 'prot_sequences_sig': '2', 
                         'pep_score': '11.50', 'prot_score': '1678', 'prot_sequences': '3', 'pep_res_after': 'D', 'prot_matches': '65', 'pep_res_before': 'K', 'pep_num_match': None, 'pep_seq': 'GAYSLSIR', 
                         'prot_mass': '54827', 'prot_desc': 'Tax_Id=9606 Gene_Symbol=FYN Isoform 3 of Tyrosine-protein kinase Fyn', 'pep_expect': '5.8', 'mz': None}]


        
        mascot = parseMascot.Reader(testFolder+'MASCOT_mzrt_in_title.xml', mz_re='([-+]?\d*\.\d+)_', rt_re='_([-+]?\d*\.\d+)')
        for i in mascot.getAssignedPeptidesMZandRTvalue():
            mzrtActual = i

        mascot = parseMascot.Reader(testFolder+'MASCOT_scan_in_title.xml', scan_re='Scan (\d+) ', file_re='(Inputfile.).RAW')
        scanActual = []
        for i in mascot.getAssignedPeptidesMZandRTvalue():
            scanActual.append(i)
            
        self.assertDictEqual(mzrtExpected, mzrtActual)
        self.assertListEqual(scanExpected, scanActual)

    def test_getAssignedPeptidesMZandRTvalueException(self):
        mascot = parseMascot.Reader(testFolder+'MASCOT_mzrt_in_title.xml')    # make a read instance#
        fail = True
        try:
            for i in mascot.getAssignedPeptidesMZandRTvalue():
                pass
        except RuntimeError:
            fail = False
        if fail:
            self.fail('RuntimeError not called for getUnassignedPeptidesMZandRTvalue')
  
    def test_getUnassignedPeptidesMZandRTvalue(self):
        mzrtExpected = {'rt': '2270.0684', 'pep_exp_z': '2', 'pep_exp_mr': '668.4303', 'scannumber': None, 'pep_num_match': None, 
                        'pep_seq': 'FLDFK', 'pep_delta': '0.0769', 'pep_miss': '0', 'pep_var_mod_pos': None, 'pep_exp_mz': '335.2224', 'fileroot': None, 
                        'pep_scan_title': '335.222412109375_2270.0684', 'pep_calc_mr': '668.3534', 'pep_var_mod': None, 'pep_score': '12.72', 'pep_expect': '4e+02', 
                        'mz': '335.222412109375'}
        
        mascot = parseMascot.Reader(testFolder+'MASCOT_mzrt_in_title.xml', mz_re='([-+]?\d*\.\d+)_', rt_re='_([-+]?\d*\.\d+)')
        for i in mascot.getUnassignedPeptidesMZandRTvalue():
            mzrtActual = i

        self.assertDictEqual(mzrtExpected, mzrtActual)

    def test_getUnassignedPeptidesMZandRTvalueException(self):
        mascot = parseMascot.Reader(testFolder+'MASCOT_mzrt_in_title.xml')    # make a read instance
        fail = True
        try:
            for i in mascot.getUnassignedPeptidesMZandRTvalue():
                pass
        except RuntimeError:
            fail = False
        if fail:
            self.fail('RuntimeError not called for getUnassignedPeptidesMZandRTvalue')
    
def suite():
    suite = unittest.TestSuite()
    # adding the unit tests to the test suite
    suite.addTest(unittest.makeSuite(testParseMascot))
    return suite

unittest.TextTestRunner(verbosity=1).run(suite())
