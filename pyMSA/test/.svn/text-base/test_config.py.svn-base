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
Unit test of config.py
"""

# author: ndeklein
# date:10/02/2012
# summary: Unit testing functionality of the config.py script


import sys 
import doctest
import os
# to be able to import unittest2 from a locally installed unittest2     * REMOVE WHEN SENDING TO OTHER USERS *
try:
    sys.path.append('/homes/ndeklein/python2.6/site-packages')
except:
    pass# some magic to import from pyMS. dirname(dirname(__file__)) gets the two directories closer to the root.
# this is so that pyMS is added to the pythonpath and you can do import config.py
# if this is made in a package from pyMS import config should also work
dirname = os.path.dirname
sys.path.append(os.path.join(dirname(dirname(__file__))))
import unittest2 as unittest
import config


class testConfig(unittest.TestCase):
    """
    A test class for the config module.
    """

        
    def test_config(self):
        configHandle = config.ConfigHandle() 
        self.assertIsInstance(configHandle, config.ConfigHandle)


def suite():
    suite = unittest.TestSuite()
    # adding the unit tests to the test suite
    suite.addTest(unittest.makeSuite(testConfig))
    return suite

    
unittest.TextTestRunner(verbosity=2).run(suite())