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
Compares information from featureXML and mzML files with eachother. 
"""

# author: ndeklein
# date:08/02/2012
# summary: Parses a featureXML file. Makes an iterator object out of the parsing (using yield, not __iter__ and __next__).

import sys 
# to be able to import pymzml from a locally installed pymzml     * REMOVE WHEN SENDING TO OTHER USERS *
try:
    sys.path.append('/homes/ndeklein/python2.6/site-packages')
except:
    pass
import pymzml
import mzmlFunctions
import parseFeatureXML
import featureFunctions
import output
import os
import warnings
import fileHandling

# compare the coordinates of the precursor (scan time and m/z) against the coordinates of the convexhull of the feature (retention time and m/z) with the mzml file
# as input and the feature file as output
# *note* the scan time is in minutes, the retention time is in seconds.
def compareCoordinate(mzmlFile, featureFile, writeCSV = False, writeTo = 'precursorPerFeature.csv'):
    r""" 
    Compare the precursors scan time and m/z values of a spectrum with all the retention time and m/z values in the convexhull of a feature. The spectrum information can come from
    a mzml File or a peaks.mzml file. It returns a dictionary with 3 keys: totalPrecursorsInFeatures, averagePrecursorsInFeatures and featPerPrecursorDict. totalPrecursorsInFeatures
    is a numeric value: the total amount of precursors that are in all features, averagePrecursorsInFeatures is a numeric value: the average amount of precursors in a feature and
    totalPrecursorsInFeatures is a dictionary with as key every feature and as value the amount of precursors per feature.
    A third input is writeCSV. If this is set to true, totalPrecursorsInFeatures is written out to a CSV file with a column featureID and a column # of precursors.
    
    @type mzmlFile: string
    @param mzmlFile: The path of the .mzML file
    @type featureFile: string
    @param featureFile: The path of the .featureXML file
    @type writeCSV: bool
    @param writeCSV: Flag if a CSV file has to be written out of the precursor per feature data (default: false)
    @type writeTo: string
    @param writeTo: The file and path where writeCSV has to be written to, default is precursorPerFeature.csv in the same folder as the script
    @rtype: Dictionary
    @returns: A dictionary with 3 keys: totalPrecursorsInFeatures, averagePrecursorsInFeatures and featPerPrecursorDict. totalPrecursorsInFeatures
    is a numeric value: the total amount of precursors that are in all features, averagePrecursorsInFeatures is a numeric value: the average amount of precursors in a feature and
    totalPrecursorsInFeatures is a dictionary with as key every feature and as value the amount of precursors per feature
    
    B{Examples}:
    
    Print the return value:

    >>> print compareCoordinate('example_mzML_file.mzML', 'example_feature_file.featureXML')
    {'totalPrecursorsInFeatures': 2, 'featPerPrecursorDict': {'f_43922326584371237334': 1, 'f_8613715360396561740': 0, 'f_13020522388175237334': 1}, 'averagePrecursorsInFeatures': 0.66666666666666663}

    Write the results to a csv file:
    
    >>> compareCoordinate(testFolder+'mzmlTestFile.mzML', testFolder+'featurexmlTestFile.featureXML', True, testFolder+'testPrecursorPerFeature.csv') # note the True
    """
    
    fileHandle = fileHandling.FileHandle(os.path.abspath(mzmlFile))
    
    # getting the absolute path of the given mzml file
    mzmlFile = os.path.abspath(mzmlFile)
    # parsing of mzml file
    msrun = pymzml.run.Reader(mzmlFile)
    
    # get the retention times and m/z of all precursors in msrun
    retentionTime = mzmlFunctions.getPrecursorRtMz(msrun)

    featureFile = os.path.abspath(featureFile)
    # make an instance of the parseFeatureXML.Reader object, with file as input
    featureXML = parseFeatureXML.Reader(featureFile)


    # featPrecursor will hold the amount of precursors per feature, with id as key and amount of precursors as feature
    featPrecursor = {}
    totalPrecursor = 0
    countZero = 0
    x = 0
    # get all features out of featureXML
    for feature in featureXML.getSimpleFeatureInfo():
        # set the amount of precursor per feature to 0 at every feature
        precursorPerFeature = 0
        # get the coordinates of all features
        featureCoordinates = featureFunctions.getFeatureConvexhullCoordinates(feature)
        # loop for every feature coordinate through every MS/MS precursor coordinate
        for mzAndRT in retentionTime:
            # if the retention time (*60 to go from minutes to seconds) is larger than xMin and smaller than xMax and the m/z is
            # larger than xMin and smaller than xMax, count the precursors
            if float(mzAndRT['rt']) * 60 > float(featureCoordinates[feature]['rtMin']) and float(mzAndRT['rt'] * 60) < float(featureCoordinates[feature]['rtMax']) \
                 and float(mzAndRT['mz']) > float(featureCoordinates[feature]['mzMin']) and float(mzAndRT['mz']) < float(featureCoordinates[feature]['mzMax']):
                precursorPerFeature += 1
                totalPrecursor += 1
        if precursorPerFeature == 0:
            countZero += 1
        featPrecursor[featureXML['id']] = precursorPerFeature
        
        x+=1

    # if writeCSV flag is set to True, write out csv file to the absolute path of writeTo (default: precursorPerFeature.csv in the same folder)
    if writeCSV:
        compareDataWriter = output.CompareDataWriter(os.path.abspath(writeTo))
        compareDataWriter.precursorPerFeatureCsvWriter(featPrecursor)

    # calculate the average precursor per feature
    averagePrecursFeature = float(totalPrecursor)/float(len(featPrecursor))
    return {'totalPrecursorsInFeatures':totalPrecursor, 'averagePrecursorsInFeatures':averagePrecursFeature, 'featPerPrecursorDict':featPrecursor}

