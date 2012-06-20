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
Example how to plot trafoXML data
"""

import sys
# for me, PyMSA_dev is not in my default python path
sys.path.append('/homes/ndeklein/workspace/MS/Trunk/PyMSA_dev')

from xml.etree import cElementTree
import rpy2.robjects as R
from pyMSA import elementFunctions
from pyMSA import parseFeatureXML
from pyMSA import getWindow  
from pyMSA import rFunctions
import collections
from pyMSA import featureMapping
from pyMSA import rPlotGenerics

def plot_trafoXML():
    """
    Plot points for the change in retention time for all the values in a .trafoXML file.
    Use the trafoXML file with as name 'linear', not 'identity'. Identity is the one that linear maps to,
    so identity doesn't have any changes.
    
    This example script uses the following classes and functions:
        - L{elementFunctions.getItems}
        - L{rPlotGenerics.Plots}

    B{Example (more detailed comments in the source code):}
    
    >>> from pyMSA import elementFunctions
    >>> from pyMSA import rPlots
    >>> import rpy2.robjects as R
    >>> changeList = []                                                                                                                    # list to keep track of the change in retention time 
    >>> for event, element in cElementTree.iterparse('example_files/input/example_trafoXML.trafoXML'):                                     # looping through all the elements in the trafoXML file
    ...    if element.tag == 'Pair':                                                                                                       # if the element == 'Pair'
    ...         changeList.append(float(elementFunctions.getItems(element)['to'])-float(elementFunctions.getItems(element)['from']))       # append the change in retention time to the changeList
    >>> changeList.sort()                                                                                                                  # sort the changeList so that the big up and down changes get grouped together
    >>> floatVector = R.FloatVector(changeList)                                                                                            # because rPlots needs R vectors, make a vector out of the list
    >>> plots = rPlots.Plots()                                                                                                             # Instantiate rPlots.Plots
    >>> plots.plot('test plot_trafoXML.png', floatVector, title='Change in retention time per feature',                                    # plot a standard plot
                    xlab='Feature number.', ylab='change in retention time')

    """
    # list to keep track of the change in retention time     
    changeList = []
    # looping through all the elements in the trafoXML file
    for event, element in cElementTree.iterparse('example_files/input/example_trafoXML.trafoXML'):
        # this part is not in the documentation example for clarity. This checks if the trafoXML file given is the right one. There are 2 trafoXML files
        # made when you align two featureXML files. One is the one of the 'identity', this one does not contain any info. The other one is 'linear', this
        # contains all the changes in retention time.
        # It exits the code  (because the identity file is useless) and gives information why.
        if element.tag == 'Transformation':
            if elementFunctions.getItems(element)['name'] == 'identity':
                sys.exit('This it he trafoXML identity file (see the Transformation node). There is no information in the identity file. Use the \'linear\' file as input')
        # if the element == 'Pair'
        if element.tag == 'Pair':
             # append the change in retention time to the changeList. The value where it comes from is substracted from the value where it goes to.
             # This way, if it changed retention time from 10000 to 11000, the change will be +1000, and when it changes retention time from 10000
             # to 9000, the change will be -1000
             changeList.append(float(elementFunctions.getItems(element)['to'])-float(elementFunctions.getItems(element)['from']))
   
    # sort the changeList so that the big up and down changes get grouped together. If the changes aren't sorted, the dots are all over the place
    changeList.sort()
    # because rPlots needs R vectors, make a vector out of the list
    floatVector = R.FloatVector(changeList)
    # Instantiate rPlots.Plots
    plots = rPlotGenerics.Plots()
    # plot a standard plot to example_files/output with the name 'test plot_trafoXML.png'. floatVector is what is plotted.
    plots.plot('example_files/output/test plot_trafoXML.png', floatVector, title='Change in retention time per feature', xlab='Feature number.', ylab='change in retention time')

def plot_trafoXML_plusFeatureIntensity():
    """
    Plot points for the change in retention time for all the values in a .trafoXML file, and change the color of the points
    according to the intensity of the feature of the original featureXML file corresponding to that point.
    Use the trafoXML file with as name 'linear', not 'identity'. Identity is the one that linear maps to,
    so identity doesn't have any changes. 
    
    This example script uses the following classes and functions:
        - L{elementFunctions.getItems}
        - L{rPlotGenerics.Plots}
        - L{rPlotGenerics.Plots.plot}
        - L{pyMSA.parseFeatureXML.Reader}
        - L{parseFeatureXML.Reader.getSimpleFeatureInfo}
        - L{rFunctions.takeLog}
        
    B{Example (see source code for additional comments):}
    
    Plot the shift in retention time of one of the featureXML files and color each point a red/blue ratio dependent on its intensity
    
    >>> from pyMSA import elementFunctions
    >>> from pyMSA import rPlots
    >>> from pyMSA import parseFeatureXML
    >>> from pyMSA import rFunctions
    >>> import rpy2.robjects as R
    >>> features_C2_01 = parseFeatureXML.Reader('/homes/ndeklein/Doreen data/featureXML/JG_TiO2_C2_01.featureXML')                             
    >>> mzDict = {}
    >>> for feature in features_C2_01.getSimpleFeatureInfo():
    ...    mzDict[str(float(round(features_C2_01['retention time'],2)))] = features_C2_01['intensity']
    >>> changeDict = collections.defaultdict(int)
    >>> for event, element in cElementTree.iterparse('/homes/ndeklein/Doreen data/trafoXML/JG_TiO2-C2_01-C2_01A-file_1.trafoXML'):
    ...    if element.tag == 'Transformation':
    ...        if elementFunctions.getItems(element)['name'] == 'identity':
    ...            sys.exit('This it he trafoXML identity file (see the Transformation node). There is no information in the identity file. Use the \'linear\' file as input')
    ...    if element.tag == 'Pair':
    ...        retentionTime = str(round(float(elementFunctions.getItems(element)['from']),2))
    ...        changeDict[float(elementFunctions.getItems(element)['to'])-float(elementFunctions.getItems(element)['from'])] = mzDict[retentionTime]
    >>> colorPalette = R.r['colorRampPalette'](R.StrVector(['red','blue']))(10)
    >>> colorVector = colorPalette
    >>> changeList = [] 
    >>> intensityList = []
    >>> for changeAndIntensity in sorted(changeDict.items()):
    ...    changeList.append(changeAndIntensity[0])
    ...    intensityList.append(changeAndIntensity[1])
    >>> for index, item in enumerate(intensityList):
    ...     intensityList[index] = colorPalette[int(rFunctions.takeLog(float(item),10)[0])]
    >>> colorVector = R.StrVector(intensityList)
    >>> floatVector = R.FloatVector(changeList)
    >>> plots = rPlots.Plots()
    >>> extraInput = {'col':colorVector,'pch':20}
    >>> plots.plot('example_files/output/test plot_trafoXML intensity.png',floatVector, width=1000, height=1000,title='Change in retention time per feature', xlab='Feature number.', ylab='change in retention time', plotArgs=extraInput)
    """    
    
    features_C2_01 = parseFeatureXML.Reader('/homes/ndeklein/Doreen data/featureXML/JG_TiO2_C2_01.featureXML')                             
    # this method is more expensive on memory, but a lot faster than old method (old method used getWindow, which looped through the list each time)
    # this makes the retention time the key value, so that the retention time can be found with O(1)
    mzDict = {}
    for feature in features_C2_01.getSimpleFeatureInfo():
        mzDict[str(round(float(features_C2_01['retention time']),8))] = features_C2_01['intensity']
    
            
    # keeps track of the amount of change between the two, with as value a list with the values of the two compared featureXML files
    changeDict = collections.defaultdict(int)
    for event, element in cElementTree.iterparse('/homes/ndeklein/Doreen data/trafoXML/JG_TiO2-C2_01-C2_01A-file_1.trafoXML'):
        if element.tag == 'Transformation':
            if elementFunctions.getItems(element)['name'] == 'identity':
                sys.exit('This it he trafoXML identity file (see the Transformation node). There is no information in the identity file. Use the \'linear\' file as input')
        if element.tag == 'Pair':
            retentionTime = str(round(float(elementFunctions.getItems(element)['from']),8))
            changeDict[float(elementFunctions.getItems(element)['to'])-float(elementFunctions.getItems(element)['from'])] = mzDict[retentionTime]

    #Create a function to generate a continuous color palette
    colorPalette = R.r['colorRampPalette'](R.StrVector(['red','blue']))(10)
    #This adds a column of color values
    # based on the intensity values
    changeList = [] 
    intensityList = []
    for changeAndIntensity in sorted(changeDict.items()):
        changeList.append(changeAndIntensity[0])
        intensityList.append(changeAndIntensity[1])

    for index, item in enumerate(intensityList):
        intensityList[index] = colorPalette[int(rFunctions.takeLog(float(item),10)[0])]
    
    colorVector = R.StrVector(intensityList)
    floatVector = R.FloatVector(changeList)
    plots = rPlotGenerics.Plots()
    extraInput = {'col':colorVector,'pch':20}
    plots.plot('example_files/output/test plot_trafoXML intensity.png',floatVector, width=1000, height=1000,title='Change in retention time per feature', xlab='Feature number.', ylab='change in retention time', plotArgs=extraInput)


def plot_mapped_and_unmapped_intensities():
    """
    Plot a boxplot of the # of features that map at each intensity.
        
    This example script uses the following classes and functions:
        - L{featureMapping.Map}
        - L{featureMapping.Map.unmappedIntensities}
        - L{featureMapping.Map.mappedIntensities}
        - L{rPlots.PlotGenerics.boxplotDataframe}
        - L{parseFeatureXML.Reader}
        - L{rFunctions.takeLog}
        - L{rFunctions.fillNA}
    
    B{Example:}
    
    >>> from pyMSA import featureMapping as fm
    >>> from pyMSA import parseFeatureXML
    >>> from pyMSA import rPlots
    >>> featureXML_1 = parseFeatureXML.Reader('/homes/ndeklein/Doreen data/featureXML/JG_TiO2_C2_01.featureXML')            
    >>> featureXML_2 = parseFeatureXML.Reader('/homes/ndeklein/Doreen data/featureXML/JG_TiO2_C2_01A.featureXML')
    >>> featuremap = featureMapping.Map(featureXML_1, featureXML_2, '/homes/ndeklein/Doreen data/trafoXML/JG_TiO2-C2_01-C2_01A-file_1.trafoXML')
    >>> unmapped_1, unmapped_2 = featureamap.unmappedIntensities()    
    >>> mapped_1, mapped_2 = featuremap.mappedIntensities()  
    >>> maxLength = len(max([unmapped_1, unmapped_2, mapped_1, mapped_2], key = len))
    >>> unmappedVector_1 = rFunctions.takeLog(R.FloatVector(rFunctions.fillNA(unmapped_1, maxLength-len(unmapped_1),'na_real')),10)
    >>> unmappedVector_2 = rFunctions.takeLog(R.FloatVector(rFunctions.fillNA(unmapped_2, maxLength-len(unmapped_2), 'na_real')),10)
    >>> mappedVector_1 = rFunctions.takeLog(R.FloatVector(rFunctions.fillNA(mapped_1, maxLength-len(mapped_1),'na_real')),10)
    >>> mappedVector_2 = rFunctions.takeLog(R.FloatVector(rFunctions.fillNA(mapped_2, maxLength-len(mapped_2), 'na_real')),10)
    >>> dataDict = {'not aligned file 1':unmappedVector_1, 'not aligned file 2':unmappedVector_2,
    ...            'aligned file 1':mappedVector_1, 'aligned file 2':mappedVector_2}
    >>> dataframe = R.DataFrame(dataDict)    
    >>> plots = rPlots.Plots()
    >>> plots.boxplotDataframe('example_files/output/intensity_of_mapped_and_unmapped.png', dataframe, title='Intensity of each aligned or non-aligned feature of two mapped featureXML files',
    ...                        xlab='', ylab='intensity of each feature', width=600, height=600)
                   
    """
    # reading the necesarry files
    featureXML_1 = parseFeatureXML.Reader('/homes/ndeklein/Doreen data/featureXML/JG_TiO2_C2_01.featureXML')            
    featureXML_2 = parseFeatureXML.Reader('/homes/ndeklein/Doreen data/featureXML/JG_TiO2_C2_01A.featureXML')
    
    # getting the FeatureMappingQuality instance
    featuremap = featureMapping.Map(featureXML_1, featureXML_2, '/homes/ndeklein/Doreen data/trafoXML/JG_TiO2-C2_01-C2_01A-file_1.trafoXML')
    # getting lists of the mapped and unmapped intensities
    unmapped_1, unmapped_2 = featuremap.unmappedIntensities()    
    mapped_1, mapped_2 = featuremap.mappedIntensities()  
    
    # get the length of the longest list, used for adding NA vlaues later
    maxLength = len(max([unmapped_1, unmapped_2, mapped_1, mapped_2], key = len))
    
    # making the vectors to go in the dataframe. Log 10 is taken of all intensities in the list. rFunctions.fillNA makes sure that all
    # vectors are of the same length before adding them to the dataframe
    unmappedVector_1 = rFunctions.takeLog(R.FloatVector(rFunctions.fillNA(unmapped_1, maxLength-len(unmapped_1),'na_real')),10)
    unmappedVector_2 = rFunctions.takeLog(R.FloatVector(rFunctions.fillNA(unmapped_2, maxLength-len(unmapped_2), 'na_real')),10)
    mappedVector_1 = rFunctions.takeLog(R.FloatVector(rFunctions.fillNA(mapped_1, maxLength-len(mapped_1),'na_real')),10)
    mappedVector_2 = rFunctions.takeLog(R.FloatVector(rFunctions.fillNA(mapped_2, maxLength-len(mapped_2), 'na_real')),10)
    
    
    dataDict = {'not aligned file 1':unmappedVector_1, 'not aligned file 2':unmappedVector_2,
                'aligned file 1':mappedVector_1, 'aligned file 2':mappedVector_2}
    dataframe = R.DataFrame(dataDict)    
    
    plots = rPlotGenerics.Plots()
    plots.boxplotDataframe('example_files/output/intensity_of_mapped_and_unmapped.png', dataframe, title='Intensity of each aligned or non-aligned feature of two mapped featureXML files',
                    xlab='', ylab='intensity', width=600, height=600)
                   
 
if __name__ == '__main__':
    plot_trafoXML()
    plot_trafoXML_plusFeatureIntensity()
    plot_mapped_and_unmapped_intensities()
    