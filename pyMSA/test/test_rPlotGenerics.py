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
Unit test of rPlotGenerics.py
"""

# author: ndeklein
# date:10/02/2012
# summary: Unit testing functionality of the rPlotGenerics.py script


import sys 
import os
# to be able to import unittest2 from a locally installed unittest2     * REMOVE WHEN SENDING TO OTHER USERS *
try:
    sys.path.append('/homes/ndeklein/python2.6/site-packages')
except:
    pass# some magic to import from pyMS. dirname(dirname(__file__)) gets the two directories closer to the root.
# this is so that pyMS is added to the pythonpath and you can do import rPlots.py
# if this is made in a package from pyMS import rPlots should also work
dirname = os.path.dirname
sys.path.append(os.path.join(dirname(dirname(__file__))))
import unittest2 as unittest
import config
import rPlotGenerics as rPlots
import warnings
import rpy2.robjects as R
import rFunctions

configHandle =  config.ConfigHandle()
config = configHandle.getConfig()
testFolder = config.get('test','testfilefolder')

class testRPlotGenerics(unittest.TestCase):
    """
    A test class for the rPlots module.
    """
    
    def setUp(self):
        self.plots = rPlots.Plots()
    
    def test_getParams(self):
        expectedDict = {'title':'changed title', 'xlab':'changed xlab', 'ylab':'y','width':600, 'height':600,'plotArgs':None}
        def exampleFunction(**kwargs):
            return self.plots.getParams(dict(kwargs))     # have to make a dictionary out of kwargs
        actualDict = exampleFunction(title='changed title', xlab = 'changed xlab') # note that in the output xlab and title change, but the rest is default

        self.assertDictContainsSubset(expectedDict, actualDict)

        Plots = rPlots.Plots()
        with warnings.catch_warnings(record=True) as warn:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            # trigger a warning
            self.plots.getParams({'get':'warning'})
            assert len(warn) == 1
            assert issubclass(warn[-1].category, UserWarning)
            assert 'Input param' in str(warn[-1].message)

    def test_getParamsExceptions(self):
         self.assertRaises(TypeError, self.plots.getParams, {'thisIsCorret':'type input'}, 'this isn not')
         self.assertRaises(TypeError, self.plots.getParams, 'this is not correct input', {'this':'is'})
         
    def test_getColors(self):
        expectedList = [{'alpha': 125, 'blue': 255, 'green': 0, 'maxColorValue': 255, 'red': 0},
                        {'alpha': 125, 'blue': 0, 'green': 0, 'maxColorValue': 255, 'red': 255},
                        {'alpha': 125, 'blue': 0, 'green': 255, 'maxColorValue': 255, 'red': 255},
                        {'alpha': 125, 'blue': 96 ,'green': 164,'maxColorValue': 255,'red': 244}]
        actualList = []
        for color in ['blue','red','yellow', ['244', '164','96']]:
            actualList.append(self.plots.getColor(color))
     
        self.assertListEqual(expectedList, actualList)
        
    def test_getColorsException(self):
        self.assertRaises(TypeError, self.plots.getColor, ('not','a','string or list'))
        self.assertRaises(ValueError, self.plots.getColor, 'not an allowed color')
        self.assertRaises(ValueError, self.plots.getColor, ['too','short'])
     
    def test_histogram(self):
        ###TEST 1 HISTOGRAM###
        # if the ouput file already exists, remove it
        if os.path.exists(testFolder+'test_histogram.png'):
            os.remove(testFolder+'test_histogram.png')
            
        # reading in a csv file, seperated by tabs into a matrix
        csvData = rFunctions.readCsvFile(testFolder+'feature.csv', sep = '\t', head=True, na='N/A')
        # get only the rows with unique ids and put it in a new matrix
        csvUniqID = rFunctions.getRowsWithUniqColumn(csvData, 'id')      
        # get a vector of all intensities using the index function from R_functions
        intensityVector = csvData[rFunctions.index(csvUniqID, 'intensity')]
        logIntensityVector = rFunctions.takeLog(intensityVector, 10)

        # using all possible **kwargs arguments to test if they are all parsed correctly
        self.plots.histogram(testFolder+'test_histogram.png', logIntensityVector, plotArgs={'labels':True}, width=400, height=400, title='test #features per intensity',  ylab = '# of test features')
        # if after this the ouput does not exist, fail the test
        if not os.path.exists(testFolder+'test_histogram.png'):
            self.fail(testFolder+'test_histogram.png does not exist. File not written out correctly')
        else:
            os.remove(testFolder+'test_histogram.png')


        ###TEST 3 HISTOGRAMS
        # if the test doesn't give an error it succeeded
        if os.path.exists(testFolder+'testOverlapHistogram.png'):
            os.remove(testFolder+'testOverlapHistogram.png') # to make sure that the test isn't passing when the method doesn't work, but the file already exists
        outpng = testFolder+'testOverlapHistogram.png'
        vector1 = R.IntVector((0,2,2,3,3,3,4,4,5))
        vector2 = R.IntVector((2,4,4,5,5,5,6,6,7))
        vector3 = R.IntVector((4,6,6,7,7,7,8,8,9))
        plots = rPlots.Plots()
        plots.histogram(outpng,vector1,vector2,vector3)
        R.r['dev.off']()
        if os.path.exists(testFolder+'testOverlapHistogram.png'):
            os.remove(testFolder+'testOverlapHistogram.png')



    def test_histogramExceptions(self):
        self.assertRaises(TypeError, self.plots.histogram, 'not an R.FloatVector', testFolder+'feature.csv', testFolder+'unreachableoutput.png')
        self.assertRaises(TypeError, self.plots.histogram, R.FloatVector((2.2,3.2,1.2)), testFolder+'feature.csv', testFolder+'unreachableoutput.png', plotArgs = 'not a dict')


    def test_barplot(self):
        # reading in a csv file, seperated by tabs into a matrix
        csvData = rFunctions.readCsvFile(testFolder+'feature_precursor.csv', head=True, sep='\t')
        # get the # precursors column and put it in a vector (R dataframe translate '#' to 'X.' and ' ' to '.'
        precursorVector = csvData[rFunctions.index(csvData, 'X..precursors')]

        precursTable = R.r['table'](precursorVector)
        # if the ouput file already exists, remove it
        if os.path.exists(testFolder+'test_barplot.png'):
            os.remove(testFolder+'test_barplot.png')
        
        self.plots.barplot(testFolder+'test_barplot.png', precursTable)
        R.r['dev.off']() 
        
        if not os.path.exists(testFolder+'test_barplot.png'):
            self.fail(testFolder+'test_barplot.png does not exist. File not written out correctly')
        else:
            os.remove(testFolder+'test_barplot.png')
        

    def test_boxplotDataframe(self):
        # if the ouput file already exists, remove it
        if os.path.exists(testFolder+'boxplotDataframe.png'):
            os.remove(testFolder+'boxplotDataframe.png')
        
        msmsPrecursorPerFeaturePerIntensity = rFunctions.readCsvFile(testFolder+'msmsPrecursorPerFeaturePerIntensity.csv', sep=',')

        self.plots.boxplotDataframe(testFolder+'boxplotDataframe.png', msmsPrecursorPerFeaturePerIntensity, width=400, height=400, 
                     			   title='feature and ms/ms per intensity', xlab = 'log 10 of intensity', ylab = '# of MS/MS per feature')
        R.r['dev.off']() 
        # if after this the ouput does not exist, fail the test
        if not os.path.exists(testFolder+'boxplotDataframe.png'):
            self.fail(testFolder+'boxplotDataframe.png does not exist. File not written out correctly')
        
        # remove the plot
        if os.path.exists(testFolder+'boxplotDataframe.png'):
            os.remove(testFolder+'boxplotDataframe.png')


    def test_boxplotDataframeExceptions(self):
        dataframe = R.DataFrame({'dataframe':1})
        self.assertRaises(TypeError, self.plots.boxplotDataframe, 'remove.png','notadataframe') 
        self.assertRaises(TypeError, self.plots.boxplotDataframe, 'remove.png', dataframe, plotArgs='not a dict')
    
        if os.path.exists('remove.png'):
            os.remove('remove.png')
    
    def test_boxplotFormulae(self):
        # if the ouput file already exists, remove it
        if os.path.exists(testFolder+'boxplotFormulae.png'):
            os.remove(testFolder+'boxplotFormulae.png')
            
        featDataframe = rFunctions.readCsvFile(testFolder+'feature.csv')
        featDataframeUniq = rFunctions.getRowsWithUniqColumn(featDataframe, 'id')
        precursorPerFeatureDataframe = rFunctions.readCsvFile(testFolder+'feature_precursor.csv', head=True, sep='\t')
        mergedFeatureDataframe = R.r['merge'](featDataframeUniq, precursorPerFeatureDataframe)
        mergedFeatureDataframe[rFunctions.index(mergedFeatureDataframe, 'intensity')] = R.r['round'](rFunctions.takeLog(featDataframeUniq[rFunctions.index(featDataframeUniq, 'intensity')], 10))
        vector1 = mergedFeatureDataframe[rFunctions.index(mergedFeatureDataframe, 'X..precursors')]
        vector2 = mergedFeatureDataframe[rFunctions.index(mergedFeatureDataframe,'intensity')]

        self.plots.boxplotFormulae(testFolder+'boxplotFormulae.png', vector1, vector2, mergedFeatureDataframe, 
                                title = 'MS/MS per feature per intensity', ylab = '# of MS/MS per feature', xlab = 'Rounded log10 of intensity')
        R.r['dev.off']() 
        # if after this the ouput does not exist, fail the test
        if not os.path.exists(testFolder+'boxplotFormulae.png'):
            self.fail(testFolder+'boxplotFormulae.png does not exist. File not written out correctly')
        # remove the plot
        if os.path.exists(testFolder+'boxplotFormulae.png'):
            os.remove(testFolder+'boxplotFormulae.png')


    def test_boxplotFormulaeException(self):
        dataframe = R.DataFrame({'dataframe':1})
        vector1 = R.IntVector([1,2,3])
        vector2 = R.FloatVector([1.1,1.2,1.3])
        self.assertRaises(TypeError, self.plots.boxplotFormulae, 'remove.png',vector1, vector2) 
        self.assertRaises(TypeError, self.plots.boxplotFormulae, 'remove.png', vector2, vector1, dataframe, plotArgs='not a dict')
        self.assertRaises(TypeError, self.plots.boxplotFormulae, 'remove.png','notavector', vector2)
        self.assertRaises(TypeError, self.plots.boxplotFormulae, 'remove.png', vector2, 'notavector')
        
        if os.path.exists('remove.png'):
            os.remove('remove.png')
        
def suite():
    suite = unittest.TestSuite()
    # adding the unit tests to the test suite
    suite.addTest(unittest.makeSuite(testRPlotGenerics))
    return suite

unittest.TextTestRunner(verbosity=1).run(suite())