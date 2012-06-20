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
Get all the information out of the config.ini file that is located in the pyMS package folder and checks for correctness (e.g if files exist etc)
"""

# author: ndeklein   (except for the OrderedDict class)
# date:02/03/2012
# summary: Getting info from the config file and checking its validity

import ConfigParser
import os
import warnings


# configParser to parse the config file
class ConfigHandle:
    """
    Methods to get information from the config file and check them for validity (if folders and files actually exist etc). 
    """
    def __init__(self, configFile=__file__.split('pyMS')[0]+'config.ini'):
        """
        Read in the config file by getting the location of baseFunctions.py, splitting everything right of pyMS and include pyMS of and adding config.ini
        Open the file to get an error if the config file can't be found at that location (because config.read() returns an empty list if it doesn't find anything)

        
        @type configFile: string
        @param configFile: The name of the config file (default = in the PyMS folder)        
        """
        open(configFile)  # open to get an error if the config file isn't there
        
        self.config = ConfigParser.ConfigParser()
        # reading config file, looking for config.ini in the parent folder where config.py is located (equal to ../config.ini on windows and linux)
        self.config.read(__file__.split('pyMS')[0]+'config.ini')
    
    def getConfig(self):
        """
        Get an instance of ConfigParser.ConfigParser()
        
        @rtype: ConfigParser.ConfigParser()
        @return: An instance of ConfigParser.ConfigParser() which contains the information from the config file
        
        """
        return self.config

