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
Unit test of test_Plots.py
"""

# author: ndeklein
# date:10/02/2012
# summary: Unit testing functionality of the test_Plots.py script


import sys 
import os
# to be able to import unittest2 from a locally installed unittest2
try:
    sys.path.append('/homes/ndeklein/python2.6/site-packages')
except:
    pass

import pymzml
# some magic to import from pyMS. dirname(dirname(__file__)) gets the two directories closer to the root.
# this is so that pyMS is added to the pythonpath and you can do import fileHandling.py
# if this is made in a package from pyMS import fileHandling should also work
dirname = os.path.dirname
sys.path.append(os.path.join(dirname(dirname(__file__))))
import unittest2 as unittest
import config
import plots
import mzmlFunctions

configHandle =  config.ConfigHandle()
config = configHandle.getConfig()
testFolder = os.path.join(os.path.dirname(__file__), config.get('test','testfilefolder'))
testDatabase = os.path.join(os.path.dirname(__file__), config.get('test', 'testdatabase'))


class testPlots(unittest.TestCase):
    """
    A test class for the fileHandling module.
    
    B{TODO:}
    
    Write some assertions to make sure the right values get inserted (some do, but some only check if there is no error when inserting)
    """
#    
#    def test_massWindow_XIC_plot(self):
#        mzmlInstance = pymzml.run.Reader(testFolder+'mzml_testFIle_withBinary.mzML')
#        retentionTime, intensity = mzmlFunctions.getIntensityFromMZwindow(mzmlInstance, 0, 2000)
#        plots.massWindow_XIC_plot(retentionTime, intensity)
##    
#    def test_massWindow_XIC_plotException(self):
#        mzmlInstance = pymzml.run.Reader(testFolder+'mzml_test_file_1.mzML')
#        self.assertRaises(TypeError, {'dummy':'dict'}, 'not a dict')
#        self.assertRaises(TypeError, 'not a dict', {'dummy':'dict'})
       
    def test_parent_to_XIC_plot(self):
        mzmlInstance = pymzml.run.Reader('/homes/dmamartin/Documents/PROTEOMICS/Cantrell/openMS/JG-C1-1A.mzML')
        plots.parent_to_XIC_plot(mzmlInstance, 1597.7015045641685, 4)
        

#    def test_parent_to_XIC_plotException(self):
#        mzmlInstance = pymzml.run.Reader(testFolder+'mzml_test_file_1.mzML')
#        self.assertRaises(TypeError, plots.massWindow_XIC_plot, 'not a pymzml.run.Reader() instance', 1200, 4)
#        self.assertRaises(TypeError, plots.massWindow_XIC_plot, mzmlInstance, 'not an int', 4)
#        self.assertRaises(TypeError, plots.massWindow_XIC_plot, mzmlInstance, 1200, 'not an int')
#    
def suite():
    suite = unittest.TestSuite()
    # adding the unit tests to the test suite
    suite.addTest(unittest.makeSuite(testPlots))
    return suite


unittest.TextTestRunner(verbosity=2).run(suite())