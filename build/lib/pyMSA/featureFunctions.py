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
Functions that get information out of a feature element
"""

# author: ndeklein
# date:08/02/2012
# summary: functions to get information from elements

import math
import elementFunctions
import warnings
import sys 

# Get all the coordinates of given feature element that are in the feature element
# return dictionary with the coordinates
def getFeatureConvexhullCoordinates(featureElement):
    """
    Get the coordinates of the corners of the convexhull of featureElement. Return a dictionary with as key the feature and as value a dictionary
    with as keys mzMax, mzMin, rtMax and rtMin. This is the maximum and minimum retention time and the maximum and minimum m/z ratio of the convexhull. These
    four points together can be seen as a rectangle, if you see each point as the corner. This does not take into account that the feature convexhulls are not
    perfect rectangles.
    
    @type featureElement: Element
    @param featureElement: A feature element
    @rtype: dictionary
    @return: Dictionary with key the feature and values the coordinates of the 4 corners of the convexhull
    @raises IOError: No convexhulls in the element
    @raises TypeError: featureElement is not of type Element
    
    B{Example}:
    
    Print the convexhull coordinates of all the features in a file:
    
    >>> import parseFeatureXML                                                 # to get the features use parseFeatureXML
    >>> featureXML = parseFeatureXML.Reader('example_feature_file.featureXML')   # make a reader instance
    >>> for feature in featureXML.getFeatures():                               # loop through all the features
    ...    print getFeatureConvexhullCoordinates(feature)                      # print the coordinates of all the feature convexhulls
    {<Element 'feature' at 0x136b9a80>: {'mzMax': '338.251376135343', 'rtMin': '5105.9217', 'rtMax': '5111.6874', 'mzMin': '336.124751115092'}}
    {<Element 'feature' at 0x136bd510>: {'mzMax': '430.197574989105', 'rtMin': '4001.7973', 'rtMax': '4017.7105', 'mzMin': '428.070943557216'}}
    {<Element 'feature' at 0x136bde40>: {'mzMax': '339.251376135343', 'rtMin': '5107.9217', 'rtMax': '5112.6874', 'mzMin': '337.124751115092'}}

    """    
    
    
    if str(type(featureElement)) == '<type \'Element\'>':
        # make a dictionary in which the corner coordinates of the feature will be saved
        featureCoordinate = {}
        countConvexhull = 0 # count the amnount of times the tage convexhull is found
        # for every element in feature element
        for element in featureElement:
            # if featureElement = convexhull
            if element.tag == 'convexhull':
                # every time that there is a new convexhull, make an empty list retentionTimeList for x coordinates and mzList for y coordinates
                retentionTimeList = []
                mzList = []
                # for every point in the convexhull element
                for pt in element:
                    # if the syntax of the convexhull is the same as syntax for version 1.8.0
                    if elementFunctions.getItems(pt) != {}:
                        # save the retention time (x-axis) and m/z (y-axis) in a list
                        try:
                            retentionTimeList.append(elementFunctions.getItems(pt)['x'])
                            mzList.append(elementFunctions.getItems(pt)['y'])
                        except:
                            sys.stdout.write('Your featureXML file is not in the format of output from version 1.8.0 or 1.7.0 FeatureFinder')
                            elementFunctions.getItems(pt)['x']
                    # else the syntax for 1.7.0 (don't have access to any other versions
                    else:
                        
                        for convex in pt:
                            # check what dim the convxhull position is (dim 0 is retention time, dim 1 = mz)
                            if int(elementFunctions.getItems(convex)['dim']) == 0:
                                retentionTimeList.append(convex.text)
                            elif int(elementFunctions.getItems(convex)['dim']) == 1:
                                mzList.append(convex.text)
                            else:
                                warnings.warn('dim in convexhull hullpoint is not 0 or 1. Value not used',stacklevel=2)
                # get the minimum and maximum values of x and y and save them
                rtMin = min(retentionTimeList)
                rtMax = max(retentionTimeList)
                mzMin = min(mzList)
                mzMax = max(mzList)
    
                #add the coordinates of the feature to the featureCoordinate
                featureCoordinate[featureElement] = {'rtMin':rtMin, 'rtMax':rtMax, 'mzMin':mzMin,'mzMax':mzMax}
                countConvexhull += 1 # add 1 for every convexhull
        
        if countConvexhull == 0:
            # raise an IO
            raise IOError, 'No convexhulls in the element, check your featureXML file'
        else:
            # return the dictionary with the coordinates of the feature
            return featureCoordinate
    else:
        raise TypeError, 'featureElement in getFeatureConvexhullCoordinates is not of type Element but of type: '+str(type(featureElement))


# Calculate how often the features overlap with each other based on X minimum, X maximum, Y minimum and Y maximum values (which gives the coordinates of a square
# with given dictionary with feature element as key and coordinate of that feature element as value
# Returns the amount of overlap
def getOverlap(featureCoordinates):
    """
    Calculate how often the features overlap with each other based on X min, X max, Y min and Y max values (which gives the coordinates of a square
    with given dictionary with feature element as key and coordinate of that feature element as value.
    
    @type featureCoordinates: dictionary
    @param featureCoordinates: A dictionary with as keys a set of features and as value a dictionary with the keys rtMin, rtMax, mzMin and mzMax. Contains the 4 corner coordinates of a convexhull
    @rtype: number
    @return: The amount of times that the convexhulls in featureCoordinates overlap with each other. 
    
    B{Example}:
    
    Print the overlap of all the feature's convexhulls in a file:
    
    >>> import parseFeatureXML                                                 # to get the features use parseFeatureXML
    >>> featureXML = parseFeatureXML.Reader('example_feature_file.featureXML')   # make a reader instance
    >>> featureDict = {}    
    >>> for feature in featureXML.getSimpleFeatureInfo():   # get all the features in featureXML and loop through them. Because the for loop gets the convexhull coordinates one at a time, the convexhulls first have to be put in one big dictionary before they can be given to getOverlap
    ...    featureDict.update(getFeatureConvexhullCoordinates(feature))        # getFeatureConvexhullCoordinates returns a dictionary, so featureDict can be updated with .update()
    >>> print getOverlap(featureDict)
    439
    """
    overlapCount = 0
    # calculate the amount of overlap
    # for every element in featureCoordinate
    for element in featureCoordinates:
        # looping again over every element in featureCoordinate(for comparison)
        for compareElement in featureCoordinates:
            # if the element is not the compareElement
            if element != compareElement:
                # if element overlaps on the left side with compareElement: x+=1
                # *note* only uses the left side because then it counts every overlap only ones (because all elements are compared to all elements)
                if featureCoordinates[element]['rtMin'] <= featureCoordinates[compareElement]['rtMin']\
                   and featureCoordinates[element]['rtMax'] >= featureCoordinates[compareElement]['rtMin']\
                   and ((featureCoordinates[element]['mzMin'] <= featureCoordinates[compareElement]['mzMax']\
                        and featureCoordinates[element]['mzMax'] >= featureCoordinates[compareElement]['mzMax'])\
                   or  (featureCoordinates[element]['mzMin'] <= featureCoordinates[compareElement]['mzMin']\
                        and featureCoordinates[element]['mzMax'] >= featureCoordinates[compareElement]['mzMin'])):
                        overlapCount+=1
    return overlapCount

