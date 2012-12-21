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
Unit test of output.py
"""

# author: ndeklein
# date:10/02/2012
# summary: Unit testing functionality of the output.py script


import sys
import os
# to be able to import unittest2 from a locally installed unittest2     * REMOVE WHEN SENDING TO OTHER USERS *
try:
    sys.path.append('/homes/ndeklein/python2.6/site-packages')
except:
    pass# some magic to import from pyMS. dirname(dirname(__file__)) gets the two directories closer to the root.
# this is so that pyMS is added to the pythonpath and you can do import output.py
# if this is made in a package from pyMS import output should also work
dirname = os.path.dirname
sys.path.append(os.path.join(dirname(dirname(__file__))))
import unittest2 as unittest
import config
import output
import csv
import parseFeatureXML
import pymzml
import compareFeatureXMLmzML as compare

configHandle =  config.ConfigHandle()
config = configHandle.getConfig()
testFolder = config.get('test','testfilefolder')


class testOutput(unittest.TestCase):
    """
    A test class for the output module.
    """
    
    def test_csvWriteLine(self):
        expectedCsvLine = ['charge', 'convexhull_xCoor', 'convexhull_yCoor', 'id', 'intensity', 'overallquality', 'position_dim0', 'position_dim1', 'quality_dim0', 'quality_dim1', 'spectrum_index', 'spectrum_native_id']
         # removing the file at the start rather than at the end incase someone wants to look at the output testfile
        if os.path.exists(testFolder+'testCsvWriteLine.csv'):
            # to make sure that the test isn't falsely passing when the method doesn't work, but the file already exists
            os.remove(testFolder+'testCsvWriteLine.csv') 
        columnList = sorted(['spectrum_index','spectrum_native_id','convexhull_yCoor','convexhull_xCoor','charge','intensity','position_dim0','position_dim1','overallquality','quality_dim0','quality_dim1','id'])
        with output.FileWriter(testFolder+'testCsvWriteLine.csv') as fw:   # FileWritere is used to open the file and close it after the indent goes back
               fw.csvWriteLine(columnList)
        actualCsvLine = csv.reader(open(testFolder+'testCsvWriteLine.csv', 'rb'), delimiter='\t').next()
 
        self.assertEqual(expectedCsvLine, actualCsvLine)
        
        os.remove(testFolder+'testCsvWriteLine.csv') 

    def test_csvWriteLineException(self):
        wrongType = 'wrong\ttype'
        with output.FileWriter(testFolder+'testCsvWriteLine.csv') as fw:   # FileWritere is used to open the file and close it after the indent goes back
               self.assertRaises(TypeError(fw.csvWriteLine, wrongType))
        os.remove(testFolder+'testCsvWriteLine.csv') 

    def test_FileWriter(self):
        expectedString = 'test file for FileWrite class in output.py\nthis writes into the same file, because it is still open'

        if os.path.exists(testFolder+'testFileWriterFile.txt'):
            # to make sure that the test isn't falsely passing when the method doesn't work, but the file already exists
            os.remove(testFolder+'testFileWriterFile.txt') 
            
        with output.FileWriter(testFolder+'testFileWriterFile.txt') as fw:
            fw.outFile.write('test file for FileWrite class in output.py\n')  # the file is open
            fw.outFile.write('this writes into the same file, because it is still open')    # the file is still open
        
        actualString = open(testFolder+'testFileWriterFile.txt').read()
        self.assertEqual(expectedString, actualString)
        os.remove(testFolder+'testFileWriterFile.txt') 
        
    def test_FileWriterException(self):
        with output.FileWriter(testFolder+'testFileWriterFile.txt') as fw:
            fw.outFile.write('test file for FileWrite class in output.py')  # the file is open
            fw.outFile.write('this writes into the same file, because it is still open')    # the file is still open
        
        self.assertRaises(ValueError, fw.outFile.write, 'if everything is correct this should give an error')
        os.remove(testFolder+'testFileWriterFile.txt') 
        
    def test_write(self):
        expectedString = 'test file for FileWrite class in output.py\nthis writes into the same file, because it is still open'

        if os.path.exists(testFolder+'testFileWriterFile.txt'):
            # to make sure that the test isn't falsely passing when the method doesn't work, but the file already exists
            os.remove(testFolder+'testFileWriterFile.txt') 
            
        with output.FileWriter(testFolder+'testFileWriterFile.txt') as fw:
            fw.write('test file for FileWrite class in output.py\n')  # the file is open
            fw.write('this writes into the same file, because it is still open')    # the file is still open
        
        actualString = open(testFolder+'testFileWriterFile.txt').read()
        
        self.assertEqual(expectedString, actualString)
        os.remove(testFolder+'testFileWriterFile.txt') 
        
        
    def test_writeException(self):
        with output.FileWriter(testFolder+'testFileWriterFile.txt') as fw:
            fw.outFile.write('test file for FileWrite class in output.py')  # the file is open
            fw.outFile.write('this writes into the same file, because it is still open')    # the file is still open
        
        self.assertRaises(ValueError, fw.write, 'if everything is correct this should give an error')

        os.remove(testFolder+'testFileWriterFile.txt') 
        
        
    def test_getInfo(self):
        expectedFeatureList = ['f_130205234428175237334','f_130205234428175237334','f_13020522388175237334','f_13020522388175237334','f_8613715360396561740','f_8613715360396561740','f_43922326584371237334', 'f_43922326584371237334']
        expectedKeyList = ['charge','intensity','charge','intensity', 'charge', 'intensity', 'charge', 'intensity']
        expectedInfoList = ['2', '52234', '2', '234284', '2', '111429', '2', '556384']
        
        actualFeatureList = []
        actualKeyList = []
        actualInfoList = []   
        actualFeatureList_fromSet = []    # differences between the two is that one actual will be made from a list and the other from a set input
        actualKeyList_fromSet = []
        actualInfoList_fromSet = []   
             
        featurexmlReaderInstance = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
        featureWriter = output.FeatureWriter(featurexmlReaderInstance)
        for featureId, key, info in featureWriter.getInfo(['charge','intensity']): # test with list
            actualFeatureList.append(featureId)
            actualKeyList.append(key)
            actualInfoList.append(info)
        for featureId, key, info in featureWriter.getInfo(set(['charge','intensity'])): #test with set
            actualFeatureList_fromSet.append(featureId)
            actualKeyList_fromSet.append(key)
            actualInfoList_fromSet.append(info)
        
        self.assertListEqual(expectedFeatureList, actualFeatureList)
        self.assertListEqual(expectedKeyList, actualKeyList)  
        self.assertListEqual(expectedInfoList, actualInfoList)
        self.assertListEqual(expectedFeatureList, actualFeatureList_fromSet)
        self.assertListEqual(expectedKeyList, actualKeyList_fromSet)  
        self.assertListEqual(expectedInfoList, actualInfoList_fromSet)
   
    def test_getInfoException(self):
        featurexmlReaderInstance = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
        featureWriter = output.FeatureWriter(featurexmlReaderInstance)
        self.assertRaises(TypeError, lambda: list(featureWriter.getInfo('notalist'))) #lambda makes sure the whole loop is run


    def test_FeatureCsvWriter(self):
        expectedCsvFirstLine = ['charge', 'convexhull_xCoor', 'convexhull_yCoor', 'id', 'intensity', 'overallquality', 'position_dim0', 'position_dim1', 'quality_dim0', 'quality_dim1', 'spectrum_index', 'spectrum_native_id']
        expectedCsvSecondLine = ['2', '5107.9217', '337.125209180674', 'f_43922326584371237334', '556384', '225053', '5107.29224', '337.251104825', '0', '0', '3916', '18484']        
        reader = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
        if os.path.exists(testFolder+'featureCsvTest.csv'):
            os.remove(testFolder+'featureCsvTest.csv') # to make sure that the test isn't passing when the method doesn't work, but the file already exists
        featureCsvWriter = output.FeatureCsvWriter(testFolder+'featureCsvTest.csv', reader)
        csvReader = csv.reader(open(testFolder+'featureCsvTest.csv', 'rb'), delimiter='\t')
        actualCsvFirstLine = csvReader.next()
        actualCsvSecondLine = csvReader.next()
            
        self.assertListEqual(expectedCsvFirstLine,actualCsvFirstLine)
        self.assertListEqual(expectedCsvSecondLine,actualCsvSecondLine)
        os.remove(testFolder+'featureCsvTest.csv')
        
        
    def test_MsrunCsvWriter(self):
        expectedFirstLine = ['total ion current', 'scan time', 'id', 'charge state', 'ms level', 'charge', 'mz', 'base peak intensity']
        expectedSecondLine = ['16675500.0', '5.8905', '19', 'N/A', '1.0', 'N/A', 'N/A', 'N/A']
        
        if os.path.exists(testFolder+'/testMsrunCsvWriter.csv'):
            os.remove(testFolder+'testMsrunCsvWriter.csv') # to make sure that the test isn't falsely passing when the method doesn't work, but the file already exists
        msrun = pymzml.run.Reader(testFolder+'mzml_test_file_2.mzML')
        copyMsrun = pymzml.run.Reader(testFolder+'mzml_test_file_2.mzML')        # needs a copy of msrun because of the design of pymzml
        writer = output.MsrunCsvWriter(testFolder+'testMsrunCsvWriter.csv', msrun)
        csvFile =  open(testFolder+'testMsrunCsvWriter.csv')
        actualFirstLine = csvFile.readline().strip('\r\n').split('\t')
        actualSecondLine = csvFile.readline().strip('\r\n').split('\t')


        self.assertSetEqual(set(expectedFirstLine), set(actualFirstLine))
        self.assertSetEqual(set(expectedSecondLine), set(actualSecondLine))
        os.remove(testFolder+'testMsrunCsvWriter.csv')
    
    
    def test_precursorPerFeatureCsvWriter(self):
        expectedFirstLine = ['id', '# precursors\r\n'] 
        expectedSecondLine = {'f_43922326584371237334': 1, 'f_8613715360396561740': 0, 'f_13020522388175237334': 1}
        
        if os.path.exists(testFolder+'featPerPrecursorCsvTest.csv'):
            os.remove(testFolder+'featPerPrecursorCsvTest.csv') # to make sure that the test isn't passing when the method doesn't work, but the file already exists
        msrun = pymzml.run.Reader(testFolder+'mzml_test_file_1.mzML')
        precursPerFeature = compare.compareCoordinate(testFolder+'mzml_test_file_1.mzML', testFolder+'featurexmlTestFile_1.featureXML')['featPerPrecursorDict']    # see compareFeatureXMLmzML.py for details
        writer = output.CompareDataWriter(testFolder+'featPerPrecursorCsvTest.csv')
        writer.precursorPerFeatureCsvWriter(precursPerFeature)
        csvFile =  open(testFolder+'featPerPrecursorCsvTest.csv')
        actualFirstLine = csvFile.readline().split('\t')
        actualSecondLine = csvFile.readline().split('\t')
        os.remove(testFolder+'featPerPrecursorCsvTest.csv')
    
def suite():
    suite = unittest.TestSuite()
    # adding the unit tests to the test suite
    suite.addTest(unittest.makeSuite(testOutput))
    return suite

unittest.TextTestRunner(verbosity=1).run(suite())