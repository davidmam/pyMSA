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
Example how to parse a featureXML file and print the convexhull of all the features
"""

# author: ndeklein
# date:28/03/2012
# summary: Example how to parse a featureXML file

# to be able to import pyMSA and without making a package (because info changes everytime during development, don't want to make a new
# package everytime) 
import sys
# for me, PyMSA_dev is not in my default python path
try:
    sys.path.append('/homes/ndeklein/workspace/MS/Trunk/PyMSA_dev')
except:
    pass

from pyMSA import parseFeatureXML


def printConvexhull():
    """
    Example how to parse a featureXML file and print the convexhull coordinates
    
    This example script uses the following classes and functions:
        - L{parseFeatureXML.Reader}
        - L{parseFeatureXML.Reader.getSimpleFeatureInfo}
 
    Printing the convexhulls
    
    >>> featureXML = parseFeatureXML.Reader('example_feature_file.featureXML')      # make a Reader instance
    >>> features = featureXML.getSimpleFeatureInfo()                                # get all the features of the Reader instance
    >>> for feature in features:                                                    # loop through all the features
        print featureXML['convexhull']                                              # print the convexhull coordinates

    """
    # make a Reader instance
    featureXML = parseFeatureXML.Reader('/homes/ndeklein/Doreen data/featureXML/JG_TiO2_C2_01.featureXML')      
    # get all the features of the Reader instance
    features = featureXML.getSimpleFeatureInfo()      
    # loop through all the features                   
    for feature in features:                                    
        print featureXML['convexhull']
        sys.exit()   

if __name__ == '__main__':
    printConvexhull()