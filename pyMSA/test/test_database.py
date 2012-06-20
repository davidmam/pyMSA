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
Unit test of database.py
"""

# author: ndeklein
# date:10/02/2012
# summary: Unit testing functionality of the database.py script


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
import database
import parseFeatureXML
import parseMascot
import MySQLdb as mdb
try:
    # to be able to import pysqlite2
    sys.path.append('/sw/opt/lib/python2.6/site-packages/')
except:
    pass
from pysqlite2 import dbapi2 as sqlite


configHandle =  config.ConfigHandle()
config = configHandle.getConfig()
testFolder = os.path.join(os.path.dirname(__file__), config.get('test','testfilefolder'))
testDatabasePath = os.path.join(os.path.dirname(__file__), config.get('test', 'testdatabase'))
import warnings

class testDatabase(unittest.TestCase):
    """
    A test class for the fileHandling module.
    
    B{TODO:}
    
    Write some assertions to make sure the right values get inserted (some do, but some only check if there is no error when inserting)
    """
    
    
    def setUp(self):

        """

        set up data used in the tests.

        setUp is called before each test function execution.

        """
    
        # Initialize the con variable to None. In case we could not create a connection to the database (for example the disk is full), we would not have a connection variable defined. This would lead to an error in the finally clause.
        self.connection = None
        try:
            import os
            # connect to the pyMS_database.db database. The connect() method returns a connection object.
            self.connection = sqlite.connect(testDatabasePath+'test_pyMSA_database.db')
            # From the connection, get the cursor object. The cursor is used to traverse the records from the result set. 

            self.cursor = self.connection.cursor()
        # In case of an exception,  print an error message and exit the script with an error code 1.
        except sqlite.Error, e:
            raise sqlite.Error, 'Error trying to connect to database: %s' % e.args[0]       
        
        # enable enforcing foreign key
        self.cursor.execute("PRAGMA foreign_keys=ON")
        # because I don't want to see warnings everytime when testing (and the test already checks if the warning is raise)
        warnings.filterwarnings('ignore')
    
        self.mysql_connection = None
        try:
            # connectionnect to the pyMS_database.db database. The connect() method returns a connection object.
            self.mysql_connection = mdb.connect('gjb-mysql-1.cluster.lifesci.dundee.ac.uk', 'ndeklein', 'm31th3amh4','test')
            # From the connection, get the cursor object. The cursor is used to traverse the records from the result set. 

            self.mysql_cursor = self.mysql_connection.cursor()    
        # In case of an exception,  print an error message and exit the script with an error code 1.
        except mdb.Error, e:
            print "Error %d: %s" % (e.args[0],e.args[1])
            sys.exit(1)

        return self
    

    def test_ConnectSqlite(self):
        # no exception means succes
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            pass

    def test_ConnectSqliteException(self): 
        self.assertRaises(IOError, database.ConnectSqlite, '/not/an/existing/database/path')


    def test_ConnectMySQL(self):
        # no exception means succes
        with database.ConnectMySQL('gjb-mysql-1.cluster.lifesci.dundee.ac.uk', 'ndeklein', 'm31th3amh4','test') as sqlCon:
            pass
                
    def sanitizeString(self):
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            fd = FillDatabase(sqlCon)
            replace = fd.sanitizeString("Fo\x00o!", "replace") # "Fo?o!"
            ignore = fd.sanitizeString("Fo\x00o!", "ignore")   # "Foo!"
        
        self.assertEqual(replace = "Fo?o!")
        self.assertEqual(ignore = "Foo!")
        
        with database.ConnectMySQL('gjb-mysql-1.cluster.lifesci.dundee.ac.uk', 'ndeklein', 'm31th3amh4','test') as sqlCon:
            fd = FillDatabase(sqlCon)
            replace = fd.sanitizeString("Fo\x00o!", "replace") # "Fo?o!"
            ignore = fd.sanitizeString("Fo\x00o!", "ignore")   # "Foo!"

        self.assertEqual(replace = "Fo?o!")
        self.assertEqual(ignore = "Foo!")
           
    def sanitizeStringError(self):
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            fd = FillDatabase(sqlCon)
            self.assertRaises(UnicodeEncodeError, fd.sanitizeString("Fo\x00o!"))  # raises UnicodeEncodeError
            self.assertRaises(UnicodeEncodeError, fd.sanitizeString(chr(0xD800))) # raises UnicodeEncodeError
    
    def test_fillMsrun(self):
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            fd = database.FillDatabase(sqlCon,'test')
            fd.fillMsrun(testFolder+'mzml_test_file_1.mzML')
        
        self.cursor.execute("SELECT msrun_name FROM `msrun`")
        self.assertEqual(self.cursor.fetchone()[0], 'test')
        
        with database.ConnectMySQL('gjb-mysql-1.cluster.lifesci.dundee.ac.uk', 'ndeklein', 'm31th3amh4','test') as sqlCon:
            fd = database.FillDatabase(sqlCon,'test')
            fd.fillMsrun(testFolder+'mzml_test_file_1.mzML')
        
        self.mysql_cursor.execute("SELECT msrun_name FROM `msrun`")
        self.assertEqual(self.mysql_cursor.fetchone()[0], 'test')
        
    def test_fillMsrunException(self):
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            fd = database.FillDatabase(sqlCon,'test')
            fd.fillMsrun(testFolder+'mzml_test_file_1.mzML')
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            fd = database.FillDatabase(sqlCon,'test')
            self.assertRaises(sqlite.IntegrityError, fd.fillMsrun,testFolder+'mzml_test_file_1.mzML')
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            fd = database.FillDatabase(sqlCon)
            self.assertRaises(RuntimeError, fd.fillMsrun, testFolder+'mzml_test_file_1.mzML')
        
        
    def test_updateDescription(self):
        # updating from within the same instance
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            fd = database.FillDatabase(sqlCon,'test')
            fd.fillMsrun(testFolder+'mzml_test_file_1.mzML')
            fd.updateDescription('update from same instance')
        
        self.cursor.execute("SELECT description FROM `msrun` WHERE msrun_name = 'test'")
        self.assertEqual(str(self.cursor.fetchone()[0]), 'update from same instance')
        
        with database.ConnectMySQL('gjb-mysql-1.cluster.lifesci.dundee.ac.uk', 'ndeklein', 'm31th3amh4','test') as sqlCon:
            fd = database.FillDatabase(sqlCon,'test')
            fd.fillMsrun(testFolder+'mzml_test_file_1.mzML')
            fd.updateDescription('update from same instance')
    
        self.mysql_cursor.execute("SELECT description FROM `msrun` WHERE msrun_name = 'test'")
        self.assertEqual(str(self.mysql_cursor.fetchone()[0]), 'update from same instance')
        
        # updating from within a different instance
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            fd = database.FillDatabase(sqlCon,'test')
            fd.updateDescription('update from different instance')
                
        self.cursor.execute("SELECT description FROM `msrun` WHERE msrun_name = 'test'")
        self.assertEqual(str(self.cursor.fetchone()[0]), 'update from different instance')
        
        with database.ConnectMySQL('gjb-mysql-1.cluster.lifesci.dundee.ac.uk', 'ndeklein', 'm31th3amh4','test') as sqlCon:
            fd = database.FillDatabase(sqlCon,'test')
            fd.updateDescription('update from different instance')
        self.mysql_cursor.execute("SELECT description FROM `msrun` WHERE msrun_name = 'test'")
        self.assertEqual(str(self.mysql_cursor.fetchone()[0]), 'update from different instance')    
    
    def test_updatedDescriptionException(self):
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            fd = database.FillDatabase(sqlCon,'test')
            # msrun_name test doesn't exist, should give RuntimeError
            self.assertRaises(RuntimeError, fd.updateDescription, 'test')
                
            # for next test, fill msrun
            fd.fillMsrun(testFolder+'mzml_test_file_1.mzML')
            veryLongDescription = 'a'*501
            # description can be only 500 chars max
            self.assertRaises(TypeError, database.FillDatabase.updateDescription, 'test', veryLongDescription)
        
        self.connection.commit()
        
    def test_fillFeatures(self):
        expectedNumResult = 4
        featureXML = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')   # make a Reader instance
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            fd = database.FillDatabase(sqlCon,'test')
            fd.fillMsrun(testFolder+'mzml_test_file_1.mzML')
            fd.fillFeatures(featureXML)
        
        actualResult = []
        for feature in featureXML.getSimpleFeatureInfo():
            self.cursor.execute("SELECT * FROM `feature` WHERE feature_id = ?", (str(featureXML['id']),))
            actualResult.append(self.cursor.fetchone())

        self.connection.commit()

        self.assertEqual(len(actualResult), expectedNumResult)

    def test_fillFeaturesException(self):
        featureXML = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')   # make a Reader instance
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            fd = database.FillDatabase(sqlCon)
            self.assertRaises(RuntimeError, fd.fillFeatures, featureXML)

    def test_fillFeatureMapping(self):
        featureXML_1 = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
        featureXML_2 = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_2.featureXML')
        trafoXML = testFolder+'featurexmlTestFile_2.trafoXML'
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            fd = database.FillDatabase(sqlCon,'test')
            fd.fillMsrun(testFolder+'mzml_test_file_1.mzML')
            fd.fillFeatures(featureXML_1)
            fd.fillFeatures(featureXML_2)
            fd.fillFeatureMapping(featureXML_1, featureXML_2,trafoXML)
               
    def test_fillFeatureMappingException(self):
        featureXML = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
        featureXML_2 = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_2.featureXML')
        trafoXML = testFolder+'featurexmlTestFile_2.trafoXML'
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            fd = database.FillDatabase(sqlCon)
            self.assertRaises(KeyError, fd.fillFeatureMapping, featureXML, featureXML_2, trafoXML)

    def test_fillSpectrum(self):
        expectedNumResult = 10
        mzMLinstance = pymzml.run.Reader(testFolder+'mzml_test_file_1.mzML', 'MS:1000527')   # make a Reader instance
        
        actualResult = []
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            fd = database.FillDatabase(sqlCon,'None')
            fd.fillMsrun(testFolder+'mzml_test_file_1.mzML')
            fd.fillSpectrum(mzMLinstance)
            self.cursor.execute("SELECT * FROM `spectrum`")
            for result in self.cursor.fetchall():
                actualResult.append(result)
        
        self.assertEqual(expectedNumResult, len(actualResult))
    
    def test_fillSpectrumException(self):
        mzMLinstance = pymzml.run.Reader(testFolder+'mzml_test_file_1.mzML')   # make a Reader instance
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            fd = database.FillDatabase(sqlCon)
            self.assertRaises(RuntimeError, fd.fillSpectrum, mzMLinstance)
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            fd = database.FillDatabase(sqlCon)
            self.assertRaises(RuntimeError, fd.fillSpectrum, mzMLinstance)

    def test_linkSpectrumToFeature(self):
        expectedNumResult = 4
        expectedResult = [(1, 2), (1, 2), (1, 4), (1, 4)]
        
        mzMLinstance = pymzml.run.Reader(testFolder+'mzml_test_file_1.mzML')   # make a Reader instance
        featureXML = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')   # make a Reader instance
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            fd = database.FillDatabase(sqlCon,'test')
            fd.fillMsrun(testFolder+'mzml_test_file_1.mzML')
            fd.fillFeatures(featureXML)
            fd.fillSpectrum(mzMLinstance)
            fd.linkSpectrumToFeature()
        
        actualResult = []
        self.cursor.execute("SELECT * FROM feature_has_MSMS_precursor")    
        for result in self.cursor.fetchall():
            actualResult.append(result)
            actualResult.append(result)
            
        self.assertEqual(expectedNumResult, len(actualResult))
        self.assertListEqual(expectedResult, actualResult)
        
    def test_linkSpectrumToFeatureException(self):
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            fd = database.FillDatabase(sqlCon)
            self.assertRaises(RuntimeError, fd.linkSpectrumToFeature)  
    
    def test_fillMascot(self):
        expectedPeptideNumResult = 2
        expectedPeptideResult = [(1,462.24009999999998,922.46569999999997, 2,923.45010000000002,-0.98440000000000005,1,20.309999999999999,75.0\
                                  ,u'K',u'CDVDIRK',u'D',u'Label:13C(6)15N(2) (K); Label:13C(6)15N(4) (R)',u'0.0000065.0',None,u'462.240142822266_751.5624'\
                                  ,3),(2,335.22239999999999,668.43029999999999,2,668.35339999999997,0.076899999999999996,0,12.720000000000001,400.0\
                                  , None,u'FLDFK',None,None,None,None,u'335.222412109375_2270.0684',4)]
        expectedProtNumResult = 2
        expectedProtResult = [(1, 462.24009999999998, 922.46569999999997, 2, 923.45010000000002, -0.98440000000000005, 1, 20.309999999999999, 75.0, u'K'\
                               , u'CDVDIRK', u'D', u'Label:13C(6)15N(2) (K); Label:13C(6)15N(4) (R)', u'0.0000065.0', None, u'462.240142822266_751.5624', 3)
                               ,(2, 335.22239999999999, 668.43029999999999, 2, 668.35339999999997, 0.076899999999999996, 0, 12.720000000000001, 400.0, None\
                               , u'FLDFK', None, None, None, None, u'335.222412109375_2270.0684', 4)]

        mzMLinstance = pymzml.run.Reader(testFolder+'mzml_test_file_1.mzML', 'MS:1000527')   # make a Reader instance
        mascot = parseMascot.Reader(testFolder+'test_mascot.xml')
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            fd = database.FillDatabase(sqlCon,'test')
            fd.fillMsrun(testFolder+'mzml_test_file_1.mzML')
            fd.fillSpectrum(mzMLinstance)
            fd.fillMascot(mascot)
            
        actualPeptideResult = []
        self.cursor.execute("SELECT * FROM `MASCOT_peptide`")
        for result in self.cursor.fetchall():
            actualPeptideResult.append(result)
        actualProteinResult = []
        self.cursor.execute("SELECT * FROM `MASCOT_protein`")
        for result in self.cursor.fetchall():
            actualProteinResult.append(result)
        
        
        self.assertEqual(expectedPeptideNumResult, len(actualPeptideResult))
        self.assertListEqual(expectedPeptideResult, actualPeptideResult)
        self.assertEqual(expectedProtNumResult, len(actualPeptideResult))
        self.assertListEqual(expectedProtResult, actualPeptideResult)

    def test_fillMascotException(self):
        mascot = parseMascot.Reader(testFolder+'test_mascot.xml')
        with database.ConnectSqlite(testDatabasePath+'test_pyMSA_database.db') as sqlCon:
            fd = database.FillDatabase(sqlCon)
            self.assertRaises(RuntimeError, fd.fillMascot, mascot)




    def tearDown(self):
        # delete the added msrun and close the connection after every test 
        self.cursor.execute("DELETE FROM `feature_has_userParam_names_has_userParam_value`")
        self.cursor.execute("DELETE FROM `feature_has_userParam_names`")
        self.cursor.execute("DELETE FROM `MASCOT_protein`")
        self.cursor.execute("DELETE FROM `MASCOT_peptide`")
        self.cursor.execute("DELETE FROM `convexhull`")
        self.cursor.execute("DELETE FROM `convexhull_edges`")
        self.cursor.execute("DELETE FROM `feature_mapping`")
        self.cursor.execute("DELETE FROM `feature_has_MSMS_precursor`")
        self.cursor.execute("DELETE FROM `MSMS_precursor`")
        self.cursor.execute("DELETE FROM `userParam_names`")
        self.cursor.execute("DELETE FROM `userParam_value`")
        self.cursor.execute("DELETE FROM `feature`")
        self.cursor.execute("DELETE FROM `spectrum`")
        self.cursor.execute("DELETE FROM `msrun`")
        self.connection.commit()
        self.connection.close()
        
        self.mysql_cursor.execute("DELETE FROM `feature_has_userParam_names_has_userParam_value`")
        self.mysql_cursor.execute("DELETE FROM `feature_has_userParam_names`")
        self.mysql_cursor.execute("DELETE FROM `MASCOT_protein`")
        self.mysql_cursor.execute("DELETE FROM `MASCOT_peptide`")
        self.mysql_cursor.execute("DELETE FROM `convexhull`")
        self.mysql_cursor.execute("DELETE FROM `convexhull_edges`")
        self.mysql_cursor.execute("DELETE FROM `feature_mapping`")
        self.mysql_cursor.execute("DELETE FROM `feature_has_MSMS_precursor`")
        self.mysql_cursor.execute("DELETE FROM `MSMS_precursor`")
        self.mysql_cursor.execute("DELETE FROM `userParam_names`")
        self.mysql_cursor.execute("DELETE FROM `userParam_value`")
        self.mysql_cursor.execute("DELETE FROM `feature`")
        self.mysql_cursor.execute("DELETE FROM `spectrum`")
        self.mysql_cursor.execute("DELETE FROM `msrun`")
        self.mysql_connection.commit()
        self.mysql_connection.close()
       
def suite():
    suite = unittest.TestSuite()
    # adding the unit tests to the test suite
    suite.addTest(unittest.makeSuite(testDatabase))
    return suite

# unittest.TextTestRunner(verbosity=2).run(suite())
