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
Examples how to extract peaks, features or spectra, from either .peaks.mzML, .featureXML or .mzML files, between a certain m/z or ry value and print their m/z - rt value.
"""
# author: ndeklein
# date:28/03/2012
# summary: Example how to extract peaks between a certain m/z value and plot a chromatochram of their m/z - rt value

# to be able to import pyMSA and without making a package (because info changes everytime during development, don't want to make a new
# package everytime) 

import sys

# for me, PyMSA_dev is not in my default python path
try:
    sys.path.append('/homes/ndeklein/workspace/MS/Trunk/PyMSA_dev')
except:
    pass
from pyMSA import parsePeaksMzML
from pyMSA import getWindow
from pyMSA import parseFeatureXML
import rpy2.robjects as R

def peaksRetrieval():
    """
    Example of how to retrieve the m/z and retention time of peaks in a window of m/z or retention time.
    
    
    This example script uses the following classes and functions:
      - L{parsePeaksMzML.Reader}
      - L{getWindow.PeakLocation}
      - L{getWindow.PeakLocation.getPeaks_mzWindow}
      - L{getWindow.PeakLocation.getPeaks_rtWindow}
    
     
    Printing the m/z and retention time of all the peaks with an m/z between 300 and 500
    
    >>> from pyMSA import parsePeaksMzML
    >>> from pyMSA import getWindow
    >>> peaks = parsePeaksMzML.Reader('example_peak_file.peaks.mzML')                                # read in the peaks file and make an instance of parsePeaksMzML.Reader class
    >>> peakLocation = getWindow.PeakLocation(peaks)                                                 # get a getWindow.PeakLocation instance with the parsePeaksMzML.Reader instance as input
    >>> for peak in peakLocation.getPeaks_mzWindow(300,500):                                         # loop through all he peaks that have an m/z between 300 and 500
    ...    print 'mz: %s, rt: %f' % (peaks['base peak m/z'], float(peaks['scan start time'])*60)     # print the m/z and rt information from each peak                            
    mz: 350.983703613281, rt: 12.288000
    mz: 348.990600585938, rt: 50.532000
    mz: 412.955871582031, rt: 573.270000
    mz: 348.990142822266, rt: 588.264000
    mz: 412.629333496094, rt: 2981.304000
    mz: 348.990112304688, rt: 2996.268000

    Printing the m/z and retention time of all the peaks with an rt between 0 and 60
    >>> from pyMSA import parsePeaksMzML
    >>> from pyMSA import getWindow
    >>> peaks = parsePeaksMzML.Reader('example_peak_file.peaks.mzML')                                # read in the peaks file and make an instance of parsePeaksMzML.Reader class
    >>> for peak in peakLocation.getPeaks_rtWindow(0,60):                                            # get a getWindow.PeakLocation instance with the parsePeaksMzML.Reader instance as input
    ...    print peaks['base peak m/z']                                                              # loop through all he peaks that have an rt between 0 and 60
    ...    print 'mz: %s, rt: %f' % (peaks['base peak m/z'], float(peaks['scan start time'])*60)     # print the m/z and rt infomration from each peak
    mz: 350.983703613281, rt: 12.288000
    mz: 348.990600585938, rt: 50.532000
    """
    # read in the peaks file and make an instance of parsePeaksMzML.Reader class
    peaks = parsePeaksMzML.Reader('example_files/input/peaks_example.peaks.mzML')
    # get a getWindow.PeakLocation instance with the parsePeaksMzML.Reader instance as input
    peakLocation = getWindow.PeakLocation(peaks)
    # loop through all the peaks that have an m/z between 300 and 500.
    for peak in peakLocation.getPeaks_mzWindow(300,500):
        # print out mz and retention time of each peak. Results form peaks are all strings, that's why peaks['base peak m/z'] is printed using %s
        print 'mz: %s, rt: %f' % (peaks['base peak m/z'], float(peaks['scan start time'])*60)
    
    # loop through all the peaks that have a retention time between 0 and 60 (THIS IS IN MINUTES)
    for peak in peakLocation.getPeaks_rtWindow(0,60):
        # print out mz and retention time of each peak. Results form peaks are all strings, that's why peaks['base peak m/z'] is printed using %s
        print 'mz: %s, rt: %f' % (peaks['base peak m/z'], float(peaks['scan start time'])*60)



def featureRetrieval():
    """
    Example of how to retrieve the m/z and retention time of features in a window of m/z or retention time.
    
    
    This example script uses the following classes and functions:
      - L{parseFeatureXML.Reader}
      - L{getWindow.FeatureLocation}
      - L{getWindow.FeatureLocation.getFeatures_mzWindow}
      - L{getWindow.FeatureLocation.getFeatures_rtWindow}
    
    
    Printing the m/z and retention time of all the peaks with an m/z between 300 and 500
    
    >>> from pyMSA import parseFeatureXML
    >>> from pyMSA import getWindow
    >>> features = parseFeatureXML.Reader('example_featureXML_file.featureXML')                          # read in the peaks file and make an instance of parseFeatureXML.Reader class
    >>> featureLocation = getWindow.FeatureLocation(features)                                            # get a getWindow.FeatureLocation instance with the parseFeatureXML.Reader instance as input
    >>> for feature in featureLocation.getFeatures_mzWindow(300,500):                                    # loop through all he features that have an m/z between 300 and 500
    ...    print 'mz: %s, rt: %f' % (features['base peak m/z'], float(features['scan start time'])*60)   # print the m/z and rt information from each feature                            
    mz: 336.251104825, rt: 5109.29224
    mz: 428.197275997, rt: 4009.58726
    mz: 337.251104825, rt: 5107.29224

    Printing the m/z and retention time of all the peaks with an rt between 0 and 60
    >>> from pyMSA import parseFeatureXML
    >>> from pyMSA import getWindow
    >>> features = parseFeatureXML.Reader('example_featureXML_file.featureXML')                          # read in the peaks file and make an instance of parseFeatureXML.Reader class
    >>> featureLocation = getWindow.FeatureLocation(features)                                            # get a getWindow.FeatureLocation instance with the parseFeatureXML.Reader instance as input
    >>> for feature in featureLocation.getFeatures_rtWindow(0,60):                                       # loop through all he features that have an rt between 0 and 360 (this in in seconds, unlike the peaks which is in minutes. Need to be changed)
    ...    print 'mz: %s, rt: %f' % (features['base peak m/z'], float(features['scan start time'])*60)   # print the m/z and rt information from each feature                            
    mz: 428.197275997, rt: 4009.58726
    """
    
    # read in the peaks file and make an instance of parseFeatureXML.Reader class
    features = parseFeatureXML.Reader('example_files/input/featureXML_example.featureXML')     
    # get a getWindow.FeatureLocation instance with the parseFeatureXML.Reader instance as input                
    featureLocation = getWindow.FeatureLocation(features)       
    # loop through all he features that have an m/z between 300 and 500                                        
    for feature in featureLocation.getFeatures_mzWindow(300,500):
        # print out mz and retention time of each feature
        print 'mz: %s, rt: %s' % (features['mz'], features['retention time'])    

    # loop through all the peaks that have a retention time between 4000 and 5000 (THIS IS IN MINUTES [YES THIS HAS TO BE CHANGED <YES I BANGED MY HEAD ON THE TABLE BECAUSE OF THIS>])
    for feature in featureLocation.getFeatures_rtWindow(4000,5000):
        # print out mz and retention time of each feature                                    
        print 'mz: %s, rt: %s' % (features['mz'], features['retention time'])  

if __name__ == '__main__':
    #peaksRetrieval()
    featureRetrieval()