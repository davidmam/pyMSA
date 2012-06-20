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
Fill the pyMS database with from featureXML, pymzml, trafoxml, peaks.mzml files.
"""

# author: ndeklein
# date:08/02/2012
# summary: fills the pyMS database

import sys
try:
    # to be able to import pysqlite2
    sys.path.append('/sw/opt/lib/python2.6/site-packages/')
except:
    pass
from pysqlite2 import dbapi2 as sqlite
import warnings    
import os
import elementFunctions
import codecs
import featureMapping as fm
import MySQLdb as mdb
import collections

class ConnectSqlite:
    """
    Connect to an sqlite database. Returns self, which can be given to FillDatabase and InteractWithDatabase. This way,
    FillDatabase can work with sqlite and mysql database (for mysql use L{ConnectMySQL})
    
    B{Example:}
    

    """
    def __init__(self, databaseName):
        """
        @type databaseName: string
        @param databaseName: The name and location of the database you want to fill. 
        @raise IOError: Database file given to databaseName does not exist        
        """
        if not os.path.exists(os.path.abspath(databaseName)):
            raise IOError, 'Database file path: \''+str(os.path.abspath(databaseName))+'\' given to FillDatabase does not exist.'
        self.databaseName = databaseName
        self.connectionType = 'sqlite'

    def __enter__(self):
        """
        Set things up using __enter__ so that __exit__ can be used. Explanation of __enter__ and __exit__ can be found http://effbot.org/zone/python-with-statement.htm (and other google places)
        

        @raise sqlite.Error: An error happened when trying to connect to the database
        """

        # Initialize the con variable to None. In case we could not create a connection to the database (for example the disk is full), we would not have a connection variable defined. This would lead to an error in the finally clause.
        self.connection = None
        try:
            # connectionnect to the pyMS_database.db database. The connect() method returns a connection object.
            self.connection = sqlite.connect(self.databaseName)
            # From the connection, get the cursor object. The cursor is used to traverse the records from the result set. 

            self.cursor = self.connection.cursor()    
        # In case of an exception,  print an error message and exit the script with an error code 1.
        except sqlite.Error, e:
            raise sqlite.Error, 'sqlite.Error trying to connect to database: %s' % e.args[0]

        return self

    def __exit__(self, type, value, traceback):
        """
        __exit__ always happens. This is used to close the connection. Explanation of __enter__ and __exit__ can be found http://effbot.org/zone/python-with-statement.htm (and other google places)
        """
        if self.connection:
            self.connection.close() 

class ConnectMySQL:
    """
    Connect to a MySQL database. Returns self, which can be given to FillDatabase and InteractWithDatabase. This way,
    FillDatabase can work with sqlite and mysql database (for sqlite use L{ConnectSqlite})
    
    B{Example:}
    
    """
    
    def __init__(self, host, user, password, database):
        """
        @type host: string
        @param host: the host, where the MySQL database is located
        @type user: string
        @param user: database user name
        @type password: string
        @param password: the user's account password
        @type database: string
        @param database: the database name
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connectionType = 'mysql'

    def __enter__(self):
        """
        Set things up using __enter__ so that __exit__ can be used. Explanation of __enter__ and __exit__ can be found http://effbot.org/zone/python-with-statement.htm (and other google places)
        

        @raise sqlite.Error: An error happened when trying to connect to the database
        """

        # Initialize the con variable to None. In case we could not create a connection to the database (for example the disk is full), we would not have a connection variable defined. This would lead to an error in the finally clause.
        self.connection = None
        try:
            # connectionnect to the pyMS_database.db database. The connect() method returns a connection object.
            self.connection = mdb.connect(self.host, self.user, self.password, self.database)
            # From the connection, get the cursor object. The cursor is used to traverse the records from the result set. 

            self.cursor = self.connection.cursor()    
        # In case of an exception,  print an error message and exit the script with an error code 1.
        except mdb.Error, e:
            print "Error %d: %s" % (e.args[0],e.args[1])
            sys.exit(1)

        return self

    def __exit__(self, type, value, traceback):
        """
        __exit__ always happens. This is used to close the connection. Explanation of __enter__ and __exit__ can be found http://effbot.org/zone/python-with-statement.htm (and other google places)
        """
        if self.connection:
            self.connection.close() 

class FillDatabase:
    """
    class with functions to fill the pyMS database. One instance fills one msrun so when creating an instance of FillDatabase you have
    to give the name of the msrun and msrun description. If the msrunName already exists it will give a warning, but it can still be used.
    This is so that the database can be updated. 
    To ensure proper closing of the connection FillDatbase uses __enter__ and __exit__ 'magic' functions and needs to be used with the with statement.
    
    B{Example:}
    
    Filling database with feature info of msrun 'example'
    
    >>> import parseFeatureXML
    >>> featureXML = parseFeatureXML.Reader('example_file.featureXML')          # make a Reader instance
    >>> with fillDatabase.FillDatabase('example', 'example description') as fd:    # make a FillDatabase instance with msrun named example, description of msrun 'example description' and default database
    ...     fd.msrun()                                         # fill the msrun table. msrun name is 'example'
    ...     fd.fillFeatures'exampleSqliteDb.db', featureXML)                        # fill the other feature tables. 

    """
    def __init__(self, connect, msrunName=None, msrunDescription=''):
        """
        @type connect: Instance of L{ConnectSqlite} or L{ConnectMySQL}
        @param connect:  Connection to a database. Returned by L{ConnectSqlite} or L{ConnectMySQL} (using with, see the classes for extra info).
        @type msrunName: string
        @param msrunName: Name of the msrun. This can be linked to spectrum info from the same msrun.
        @type msrunDescription: string
        @param msrunDescription: A semi-long (max 500 chars) description of the msrun
        @raise TypeError: msrun description too long
        @raise TypeError: connect not of type L{ConnectSqlite} or L{ConnectMySQL}
        @raise Warning: msrunName is None
        """        
        if len(msrunDescription) > 500:
            raise TypeError, 'Your msrun description is too long'
        if msrunName == None:
            warnings.warn('msrunName is None. Not all functions will work. ') 
        if not isinstance(connect, ConnectSqlite) and not isinstance(connect, ConnectMySQL):
            raise TypeError, 'connect given to FillDatabase is not of type ConnectSqlite or ConnectMySQL. Instead, is of type: '+str(type(connect))
        self.connect = connect
        if connect.connectionType == 'sqlite':
            # enable forcing foreign keys for sqlite
            self.connect.cursor.execute("PRAGMA foreign_keys=ON")
            self.placeholder = '?'
        elif connect.connectionType == 'mysql':
            self.placeholder = '%s'
        
        self.connect = connect
        self.msrunName = msrunName
        self.msrunDescription = msrunDescription
        
        # bools to keep track if which tables have been filled already
        self.msrunFilled = False
        
        # to keep track through different functions of the msrunId later on
        self.msrun_primaryKey = None
        
        # lists to keep track of all the features and spectra rt and mz values inserted for faster mapping between features and MS/MS precursors (sacrifice memory for speed)
        self.featureList = []
        self.spectraList = []
       
        self.connect.cursor.execute("SELECT msrun_id FROM `msrun` WHERE msrun_name = "+self.placeholder+"",  (str(self.msrunName),))

        # check if the msrun name already exists in the database by selecting on the msrunName and if fetchone returns something
        # the name already exists
        # this is done in __enter__ instead of __init__ because __init__ is called first so self.cur doesn't exist in __init__ yet.  
        msrun_id = self.connect.cursor.fetchone()
        if msrun_id != None:    
            # warn when msrunName is already in the database
            warnings.warn('That msrun name \''+str(self.msrunName)+'\'is already used in the database. If you did not know this, make sure you want to add data to this already existing msrun.')
            # set msrunFilled to True, this is used later in fillMsrun to know if the name already exists
            self.msrunFilled = True
            self.msrun_primaryKey = msrun_id[0]
        

        # this is for speed reasons (see http://stackoverflow.com/questions/1711631/how-do-i-improve-the-performance-of-sqlite)
        # it does mean that if a machine powers down unexpectedly the db can become corrupted
        #self.cursor.execute("PRAGMA synchronous=OFF")

    def sanitizeString(self, string, errors="strict"):
        """
        Way to sanitize query input. Use this if you want to use variable table or column names (as used in getPrimaryKeyValue). For variable values use the sqlite's "+self.placeholder+" method.
        This code is a direct copy from http://stackoverflow.com/a/6701665/651779, read that for more information (and to give credits).
        
        {Example:}
        
        >>> with fillDatabase.FillDatabase'exampleSqliteDb.db','test', 'this is a test input. should be deleted after use') as fd:
        ...     print fd.sanitizeString("Fo\x00o!", "replace")
        "Fo?o!"
        ...     print fd.sanitizeString("Fo\x00o!", "ignore")   
        "Foo!"
        """
        encodable = string.encode("utf-8", errors).decode("utf-8")

        nul_index = encodable.find("\x00")

        if nul_index >= 0:
            error = UnicodeEncodeError("NUL-terminated utf-8", encodable,
                              nul_index, nul_index + 1, "NUL not allowed")
            error_handler = codecs.lookup_error(errors)
            replacement, _ = error_handler(error)
            encodable = encodable.replace("\x00", replacement)

        return encodable

    def getPrimaryKeyValue(self, column, table, sanitize=False):
        """
        Gets the value for the primary key of column and table. Selects max of column and adds one. The primary key value returned is always
        1 higher than the highest value currently in column of table. If there is no current value (it's the first entry) the value is set to 1.
        This works on all tables and columns that are in the database to which fillDatabase is connected. The variable table and column names are 
        sanitized using L{FillDatabase.sanitizeString} before being concatenated.
        
        @type table: string
        @param table: table from which you want to get the next primary key value
        @type column: string
        @param column: name of the column that is the primary key of table.
        @type sanitize: bool
        @param sanitize: Bool to indicate if the column names should be sanitized or not. By default it is False for performance reasons, can be turned off for safety reasons
        @rtype: number
        @return: The next primary key value (one higher than the current highest primary key value)
        @raise sqlite.OperationalError: No such table or column
        
        B{Example:}
        tablename
        Get the next primary key value out of the table 'example' from database 'example_db.db' that has column 'id' and 'value'. Column 'id' is the primary key and the table looks like this:
        
        id    value
        _______________
        1     'example'
        2     'example'
        3     'examples'
        
        And the table test has to be in the database given to FillDatabase.
        
        >>> with FillDatabase('exampleSqliteDb.db', msrunName = 'example' ) as fd:
        ...    print fd.getPrimaryKeyValue('example', 'id')
        4
        """
        # select highest value of the primary key column
        if sanitize:
            self.connect.cursor.execute("SELECT max(%s) FROM `%s`" % (self.sanitizeString(column), self.sanitizeString(table)))
        else:
            self.connect.cursor.execute("SELECT max(%s) FROM `%s`" % (column, table))

        primaryKey = self.connect.cursor.fetchone()[0]
        if primaryKey == None:
            primaryKey = 0
        # add one to the max vlaue
        primaryKey += 1
        return primaryKey


    def fillMsrun(self, mzmlPath):
        """
        Fill the msrun table. If msrun already exists raise an error.
        
        @raise sqlite.IntegrityError: The name msrunName already exists in the database
        @raise RuntimeError: msrunName is None
        
        B{Example:}
        
        >>> with fillDatabase.FillDatabase'exampleSqliteDb.db', 'example', 'example description') as fd:    # make a FillDatabase instance with msrun named example, description of msrun 'example description' and default database
        ...     fd.msrun()                                         # fill the msrun table. msrun name is 'example'
        """
        # if the name already exists raise an integrity error. Name is the primary key, so can only be one of
        if self.msrunFilled:
            raise sqlite.IntegrityError, 'The name: '+str(self.msrunName)+' already exists in the table msrun. Choose a different name or, if you want to update the description, use FillDatabase.updateDescription()'
        if self.msrunName == None:
            raise RuntimeError, 'msrunName is set to None (this is also the default). You cannot fill msrun if msrunName is None. '
        self.msrun_primaryKey = self.getPrimaryKeyValue('msrun_id', 'msrun')
        # get the start time. Because it is in the start of the file, looping through the lines to find it does not take much time
        with open(mzmlPath) as mzml:
            for line in mzml:
                if 'startTimeStamp' in line:
                    startTimeStamp = line.split('startTimeStamp="')[1].split('"')[0].replace('T',' ').rstrip('Z')
                    break
        # tulip of the input values for sql insert
        inputValues = (self.msrun_primaryKey, str(self.msrunName), str(self.msrunDescription), str(startTimeStamp))
        # insert the values into msrun using "+self.placeholder+" for sql injection safety
        self.connect.cursor.execute("INSERT INTO `msrun` VALUES("+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+")", inputValues)
        # set msrunFilled to true incase someone tries to insert this name again from the same instance, or wants to update from the same instance
        self.msrunFilled = True
        # save the data 
        self.connect.connection.commit()

    def updateDescription(self, description):
        """
        Update the description of msrun. This can either be done from the same instance that msrun was added with, or with a new instance if it has an msrun_name that is already in the database.
        
        @type description: string
        @param description: A semi-long (max 500 chars) description of the msrun
        @raise TypeError: msrun description too long
        @raise RuntimeError: There is no record of msrunName in the database or msrunName = None

        B{Examples:}
        
        Updating description from the same instance:
        
        >>> with fillDatabase.FillDatabase('exampleSqliteDb.db', 'example', 'example description') as fd:    # make a FillDatabase instance with msrun named example, description of msrun 'example description' and default database
        ...     fd.msrun()                                   # fill the msrun table. msrun name is 'example'
        ...     fd.updateDescription('updated description')  # updated the description from the same instance of FillDatabase
        
        Updating description from a different instance:
        
        >>> with fillDatabase.FillDatabase('exampleSqliteDb.db', 'example', 'example description') as fd:    # make a FillDatabase instance with msrun named example, description of msrun 'example description' and default database
        ...     fd.msrun()                                       # fill the msrun table. msrun name is 'example'
        >>> with fillDatabase.FillDatabase('example') as fd:     # make a new instance with the same msrun_name
        ...     fd.updateDescription('updated description')      # updated the description from a different instance of FillDatabase

        """
        # database length of description is VARCHAR(500) so can't be longer than 500
        if len(description) > 500:
            raise TypeError, 'Your msrun description given to upodateDescription is too long'
        # can only update if the msrunName exists in the datbaase
        if not self.msrunFilled:
            raise RuntimeError, 'The msrun name \''+str(self.msrunName)+'\' given to updateDescription does not exist yet. Can not update something that does not exist'
        if self.msrunName == None:
            raise RuntimeError, 'msrunName is set to None (this is also the default). You cannot update descriotion if msrunName is None. '

        # tulip of the input values for sql insert
        msrunInputValues = (str(description), str(self.msrunName))
        # insert the values into msrun using "+self.placeholder+" for sql injection safety
        self.connect.cursor.execute("UPDATE `msrun` SET description = "+self.placeholder+" WHERE msrun_name = "+self.placeholder+"", msrunInputValues)
        self.connect.connection.commit()
        
        
    def fillFeatures(self, featureXMLinstance, intensity_cutoff = 0):
        """
        Fill all tables related to features with data from featureXMLinstance. 
        This includes the tables:
            - feature
            - position
            - convexhull
            - feature_has_userParam_names
            - userParam_names
            - feature_has_userParam_names_has_userParam_value
            - userParam_value
        
        @type featureXMLinstance: parseFeatureXML.Reader
        @param featureXMLinstance: Instance of parseFeatureXML, from which the information will be added to the database
        @type intensity_cutoff: float
        @param intensity_cutoff: The intensity cut-off for the feature picking software. (default = 0) 
        @raise RuntimeError: There is no database entry with self.msrunName as msrun_name or self.msrunName = None
        
        B{Example:}
        
        >>> import parseFeatureXML
        >>> featureXML = parseFeatureXML.Reader('example_file.featureXML')          # make a Reader instance
        >>> fillDatabaseInstance = FillDatabase('example')                          # make a FillDatabase instance with msrun named example
        >>> with fillDatabase.FillDatabase('exampleSqliteDb.db', 'example', 'example description') as fd:
        ...     fd.fillMsrun                                       # need to fill the msrun table first
        ...     fd.fillFeatures(featureXML)                        # fill the database. msrun name is 'example'
        """
        # if the msrunName given to FillDatabase() is not in the database, raise runtime error. Because feature table is linked to msrun with a foreign key, msrun HAS to be filled first
        if not self.msrunFilled:
            raise RuntimeError, 'There is no record of: \''+str(self.msrunName)+'\' in the msrun table. Run FillDatabase.fillMsrun first'
        if not isinstance(intensity_cutoff, int) and not isinstance(intensity_cutoff, float):
            raise TypeError, 'intensity_cutoff is not of type int or float. Instead, \''+str(intensity_cutoff)+'\' is of type: '+str(type(intensity_cutoff))
        if self.msrunName == None:
            raise RuntimeError, 'msrunName is set to None (this is also the default). You cannot fill features if msrunName is None. '
        self.connect.cursor.execute('begin')
        # loop through all the features and get all the info. for every feature, insert the info into the feature table        
        for feature in featureXMLinstance.getSimpleFeatureInfo():
            # getting all the necesarry info for the 'feature' table
            featureID = str(featureXMLinstance['id'])
            intensity = float(featureXMLinstance['intensity'])
            overallQuality = float(featureXMLinstance['overallquality'])
            charge = int(featureXMLinstance['charge'])
            content = str(featureXMLinstance['content'])
            msrun_msrun_name = str(self.msrunName)
            
            feature_primaryKey = self.getPrimaryKeyValue('feature_table_id', 'feature')
            # tulip of the input values for sql insert            
            featureInputValues = (feature_primaryKey, featureID, intensity, overallQuality, charge, content, intensity_cutoff, self.msrun_primaryKey)
            # insert the values into msrun using "+self.placeholder+" for sql injection safety
            
            self.connect.cursor.execute("INSERT INTO `feature` VALUES("+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+")", featureInputValues)
            # keep track of the rt and mz minimum and maximum to save the corners of the convexhull. This is used
            # for fast(er) comparison between features and spectra instead of having to get max(rt) using the db
            rtMin = 0
            rtMax = 0
            mzMin = 0
            mzMax = 0 
            # loop through all the values in the convexhull and add them to the convexhull table
            for mz_and_rt in featureXMLinstance['convexhull']:
                # increment the max value of convexhull_id by one as primary key
                covexhull_primaryKey = self.getPrimaryKeyValue('convexhull_id','convexhull')

                # fill convexhull, (SELECT max(a) FROM t1)+1 mak
                convexhullInputValues = (covexhull_primaryKey, mz_and_rt['mz'], mz_and_rt['rt'], feature_primaryKey)
                self.connect.cursor.execute("INSERT INTO `convexhull` VALUES ("+self.placeholder+","+self.placeholder+", "+self.placeholder+", "+self.placeholder+")",convexhullInputValues)
            
            self.connect.cursor.execute("SELECT min(rt), max(rt), min(mz), max(mz) FROM convexhull WHERE feature_feature_table_id = "+self.placeholder+"",(feature_primaryKey,))
            edges = self.connect.cursor.fetchone()
            convexhull_edges_inputValues = (feature_primaryKey, edges[0], edges[1], edges[2],edges[3])
            # update feature table with the convexhull edges
            
            self.connect.cursor.execute("INSERT INTO convexhull_edges VALUES("+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+")",convexhull_edges_inputValues )
            self.featureList.append([mzMin, mzMax, rtMin, rtMax, feature_primaryKey])
            # loop through all the positions and add them to thep position table
            for userParam in featureXMLinstance['userParam']:
                userParamName_primaryKey = self.getPrimaryKeyValue('userParamName_id','userParam_names')
                # input for userParam_names
                userParamNamesInputValues =  (userParamName_primaryKey, userParam['name'])
                
                self.connect.cursor.execute("INSERT INTO `userParam_names` VALUES ("+self.placeholder+","+self.placeholder+")",userParamNamesInputValues)

                # increment the max value of userParam_names by one as primary key
                userParamValue_primaryKey = self.getPrimaryKeyValue('userParamValue_id', 'userParam_value')
                # input for userParam_names
                userParamValueInputValues =  (userParamValue_primaryKey, userParam['value'])
                
                self.connect.cursor.execute("INSERT INTO `userParam_value` VALUES ("+self.placeholder+","+self.placeholder+")", userParamValueInputValues)
                # increment the max value of userParam_names by one as primary key
                feature_has_userParam_names_primaryKey = self.getPrimaryKeyValue('feature_has_userParam_names_id', 'feature_has_userParam_names')
            
                # fill the many-to-many linking tables
                featureHasUserParamValuesInputValues = (feature_has_userParam_names_primaryKey, feature_primaryKey, userParamName_primaryKey)
                self.connect.cursor.execute("INSERT INTO `feature_has_userParam_names` VALUES ("+self.placeholder+","+self.placeholder+","+self.placeholder+")", featureHasUserParamValuesInputValues)
                
                featureHasUserParamNameHasUserParamValue_inputValues = (feature_has_userParam_names_primaryKey, userParamValue_primaryKey)
                self.connect.cursor.execute("INSERT INTO `feature_has_userParam_names_has_userParam_value` VALUES ("+self.placeholder+","+self.placeholder+")", featureHasUserParamNameHasUserParamValue_inputValues)
            
        self.connect.connection.commit()
     
    def fillFeatureMapping(self, featureXMLinstance_1, featureXMLinstance_2, trafoXML_file):
        """
        Fill the featureMapping table.

        @type featureXMLinstance_1: parseFeatureXML.Reader
        @param featureXMLinstance_1: Instance of parseFeatureXML with 1 of the featureXML files used for the alignment as input for parseFeatureXML 
        @type featureXMLinstance_2: parseFeatureXML.Reader
        @param featureXMLinstance_2: Instance of parseFeatureXML with the other one of the featureXML files used for the alignment as input for parseFeatureXML
        @type trafoXML_file: string
        @param trafoXML_file: path to the trafoXML file corresponding to the aligning of the two given featureXML instances. Has to be the linear trafoXML file.
        @raise RuntimeError: There is no database entry with self.msrunName as msrun_name
        
        B{Example:}
        
        >>> import featureMapping
        >>> featureXML_1 = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_1.featureXML')
        >>> featureXML_2 = parseFeatureXML.Reader(testFolder+'featurexmlTestFile_2.featureXML')
        >>> trafoXML = testFolder+'featurexmlTestFile_2.trafoXML'
        >>> with fillDatabase.FillDatabase('exampleSqliteDb.db', 'example', 'example description') as fd:
        ...     fd.fillMsrun()
        ...     fd.fillFeatures(featureXML_1)
        ...     fd.fillFeatures(featureXML_2)
        ...     fd.fillFeatureMapping(trafoXML)
        """
        # if the msrunName given to FillDatabase() is not in the database, raise runtime error. Because feature table is linked to msrun with a foreign key, msrun HAS to be filled first
        # msrunName can be None, in which case msrunFilled doesn't have to be true, this can be used for fillFeatureMapping and feature_spectrum_linking because these can be done independently of msrun
        if not self.msrunFilled and not self.msrunName == None and not self.msrunName.lower() == 'none':
            raise RuntimeError, 'There is no record of: \''+str(self.msrunName)+'\' in the msrun table. Run FillDatabase.fillMsrun first'
       
        self.connect.cursor.execute('begin')
        featureMapping = fm.Map(featureXMLinstance_1, featureXMLinstance_2, trafoXML_file)
        self.connect.cursor.execute("SELECT feature_table_id, feature_id FROM `feature`")
        feature_dict = {}
        for feature_ids in self.connect.cursor.fetchall():
            feature_dict[feature_ids[1]] = feature_ids[0]
            if len(feature_ids) == 0:
                raise RuntimeError, 'No features found in table feature. Are you sure you are connecting to the right database table"+self.placeholder+"'
            
        for featureID_dict in featureMapping.getMappedFeatureIds():
            feature_mapping_primaryKey = self.getPrimaryKeyValue('feature_mapping_id','feature_mapping')
            # have to get the feature_table_id where the feature_id = the same as the from id, and the msrun_id is the same as self.msrun_primaryKey
            #feature_got_mapped_id_inputValues = (featureID_dict['from_featureID'],)
            #self.cursor.execute("SELECT feature_table_id FROM `feature` WHERE feature_id = "+self.placeholder+" ",feature_got_mapped_id_inputValues)    #this is the feature to which got mapped. 
            feature_got_mapped_id = feature_dict[featureID_dict['from_featureID']]
            # have to get the feature_table_id where the feature_id = the same as the to id, and the msrun_id is the same as self.msrun_primaryKey
            #feature_identity_id_inputValues = (featureID_dict['to_featureID'],) 
            #self.cursor.execute("SELECT feature_table_id FROM `feature` WHERE feature_id = "+self.placeholder+"",feature_identity_id_inputValues)    #this is the feature to which got mapped. 
            feature_identity_id = feature_dict[featureID_dict['to_featureID']]
            to_value = featureID_dict['to']
            from_value = featureID_dict['from']
            feature_mapping_inputValues = (feature_mapping_primaryKey, feature_got_mapped_id, feature_identity_id, to_value, from_value)
            self.connect.cursor.execute("INSERT INTO `feature_mapping` VALUES ("+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+")", feature_mapping_inputValues)
        self.connect.connection.commit()
    
    def fillSpectrum(self, mzMLinstance):
        """
        Fill all tables related to spectra with data from mzMLinstance. 
        This includes the tables:
            - spectrum
            - MSMS_precursor
            - spectrum_has_feature

        @type mzMLinstance: pymzml.run.Reader
        @param mzMLinstance: Instance of pyMZML.run.Reader, from which the information will be added to the database
        @raise RuntimeError: There is no database entry with self.msrunName as msrun_name
        
        B{Example:}
        
        >>> import pymzml
        >>> mzMLinstance = pymzml.run.Reader('example_file.mzML')          # make a pymzml.run.Reader instance
        >>> fillDatabaseInstance = FillDatabase('example')                          # make a FillDatabase instance with msrun named example
        >>> with fillDatabase.FillDatabase('exampleSqliteDb.db', 'example', 'example description') as fd:
        ...     fd.fillMsrun                                       # need to fill the msrun table first
        ...     fd.fillSpectrum(mzMLinstance)                        # fill the database. msrun name is 'example'
        """
        # if the msrunName given to FillDatabase() is not in the database, raise runtime error. Because feature table is linked to msrun with a foreign key, msrun HAS to be filled first
        if not self.msrunFilled:
            raise RuntimeError, 'There is no record of: \''+str(self.msrunName)+'\' in the msrun table. Run FillDatabase.fillMsrun first'
        if self.msrunName == None:
            raise RuntimeError, 'msrunName is set to None (this is also the default). You cannot fill spectrum if msrunName is None. '
        self.connect.cursor.execute('begin')
        for spectrum in mzMLinstance:
            spectrum_primaryKey = self.getPrimaryKeyValue('spectrum_id', 'spectrum')
            spectrum_index = spectrum['id']
            binary_data_mz = spectrum['encodedData'][0]
            binary_data_rt = spectrum['encodedData'][1]
                
            # apareantly not all mzml files have an ion injection time, to prevent an error, ion injetion time is initialized here already
            ion_injection_time = None
            
            # because not all values can be gotten directly, use spectrum.xmlTree. I use if for all values, even though you can also do spectrum['id'], because IMO it is more clear this way
            # it's only not used for spectrum['id'] and spectrum['encoded data'] because these do not have a 'name'
            for element in spectrum.xmlTree:
                elementInfo = elementFunctions.getItems(element)
                # everything after this needs a name in the element, if not, continue with the next element
                if not elementInfo.has_key('name'):
                    continue

                if element.tag.endswith('scanList'):
                    for items in elementFunctions.getAllNestedItems(element):
                        if items['name'] == 'ion injection time':
                            ion_injection_time = float(items['value']) / 1000 # convert from miliseconds to seconds
                           
                # so that it doesn't go through all the if and elif statements when the tag is scanList
                else:
                    if elementInfo['name'] == 'ms level':
                        ms_level = elementInfo['value']
                    elif elementInfo['name'] == 'base peak m/z':
                        base_peak_mz = elementInfo['value']
                    elif elementInfo['name'] == 'base peak intensity':
                        base_peak_intensity = elementInfo['value']
                    elif elementInfo['name'] == 'total ion current':
                        total_ion_current = elementInfo['value']
                    elif elementInfo['name'] == 'lowest observed m/z':
                        lowest_observed_mz = elementInfo['value']
                    elif elementInfo['name'] == 'highest observed m/z':
                        highest_observed_mz = elementInfo['value']
                    elif elementInfo['name'] == 'scan start time':
                        scan_start_time = float(elementInfo['value'])*60     # make seconds out of the minutes, to equalize with retention time
                    elif elementInfo['name'] == 'ion injection time': 
                        ion_injection_time = elementInfo['value']     
                     
                # because all info for MSMS_precursor is in the element, to prevent extra looping get all the values for the MSMS_precursor table now
                if int(ms_level) >= 2:
                    precursor_primaryKey = self.getPrimaryKeyValue('precursor_id','MSMS_precursor')
                    if elementInfo['name'] == 'selected ion m/z':
                        ion_mz = elementFunctions.getItems(element)['value']
                    elif elementInfo['name'] == 'charge state':
                        charge_state = elementFunctions.getItems(element)['value']
                    elif elementInfo['name'] == 'peak intensity':
                        peak_intensity = elementInfo['value']
                        
            # to prevent sql injections, put all the values in a tuple and use "+self.placeholder+" replacemenet    
            spectrum_inputValues = (spectrum_primaryKey, spectrum_index, ms_level, base_peak_mz, base_peak_intensity, total_ion_current, lowest_observed_mz, highest_observed_mz,
                                    scan_start_time, ion_injection_time, binary_data_mz, binary_data_rt, self.msrun_primaryKey)
            self.connect.cursor.execute("INSERT INTO `spectrum` VALUES ("+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+")", spectrum_inputValues)
            
            if int(ms_level) >= 2:
                MSMS_precursor_inputValues = (precursor_primaryKey, ion_mz, charge_state, peak_intensity, spectrum_primaryKey)               
                self.connect.cursor.execute("INSERT INTO `MSMS_precursor` VALUES ("+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+")", MSMS_precursor_inputValues)
                self.spectraList.append([ion_mz, scan_start_time, precursor_primaryKey])
                    
        self.connect.connection.commit()
    
    def linkSpectrumToFeature(self):
        """
        Fills the spectrum_has_feature table. Takes the spectrum and features that have the same msrun_msrun_id (the foreign key to the msrun table) and matches the ones where the
        spectrum is inside the features convexhull. 
        
        @raise RuntimeError: msrun, spectrum or feature table has not been filled yet. 
        
        B{Example:}
        
        >>> import pymzml
        >>> import parseFeatureXML
        >>> mzMLinstance = pymzml.run.Reader('example_file.mzML')                   # make a pymzml.run.Reader instance
        >>> featureXML = parseFeatureXML.Reader('example_file.featureXML')          # make a parseFeatureXML.Reader instance
        >>> fillDatabaseInstance = FillDatabase('example')                          # make a FillDatabase instance with msrun named example
        >>> with fillDatabase.FillDatabase('exampleSqliteDb.db', 'example', 'example description') as fd:
        ...     fd.fillMsrun                                                        # need to fill the msrun, feature and spectrum tables first
        ...     fd.fillSpectrum(mzMLinstance)                                      
        ...     fd.fillFeatures(featureXML)
        ...     fd.linkSpectrumToFeature()
        """    
        # if the msrunName given to FillDatabase() is not in the database, raise runtime error. Because feature table is linked to msrun with a foreign key, msrun HAS to be filled first
        # msrunName can be None, in which case msrunFilled doesn't have to be true, this can be used for fillFeatureMapping and feature_spectrum_linking because these can be done independently of msrun
        if not self.msrunFilled and not self.msrunName == None:
            raise RuntimeError, 'There is no record of: \''+str(self.msrunName)+'\' in the msrun table. Run FillDatabase.fillMsrun() first'
        if self.msrunName == None:
            raise RuntimeError, 'msrunName is set to None (this is also the default). You cannot link feature to MSMS precursors if msrunName is None. '

        self.connect.cursor.execute('begin')
        self.connect.cursor.execute("SELECT msrun_id FROM `msrun` WHERE msrun_name = "+self.placeholder+"", (self.msrunName,))
        # getting the msrun_id out of the fetchone(). Fetchone returns a tuple containing one value, want to have that value. Thus the [0]
        msrun_id = self.connect.cursor.fetchone()[0]
        
        # input values for the query that retrieves the spectrum_id and feature_table_id for all the spectrums and features where the spectrum is inside the 
        # convexhull of the feature
        spectrumFeature_InputValues = (msrun_id,msrun_id)
        
        # query that retrieves the spectrum_id and feature_table_id for all the spectrums and features where the spectrum is inside the 
        # convexhull of the feature.
        self.connect.cursor.execute("SELECT precursor_id, feature_table_id "+
                                    "FROM `MSMS_precursor` "+
                                    "JOIN `spectrum` ON spectrum_id = spectrum_spectrum_id "+
                                    "JOIN `feature` ON feature.msrun_msrun_id = spectrum.msrun_msrun_id "+
                                    "JOIN `convexhull_edges` ON convexhull_edges.feature_feature_table_id = feature.feature_table_id "
                                    "WHERE spectrum.scan_start_time BETWEEN convexhull_edges.rtMin AND convexhull_edges.rtMax "+
                                    "AND MSMS_precursor.ion_mz BETWEEN convexhull_edges.mzMin AND convexhull_edges.mzMax "+
                                    "AND feature.msrun_msrun_id = "+self.placeholder+" AND spectrum.msrun_msrun_id = "+self.placeholder+"", spectrumFeature_InputValues)
        
        precursorFeatureIds = self.connect.cursor.fetchall()
        for precursorAndFeatureID in precursorFeatureIds:
            feature_has_MSMS_precursor_inputValues = (precursorAndFeatureID[0], precursorAndFeatureID[1])
            self.connect.cursor.execute("INSERT INTO `feature_has_MSMS_precursor` VALUES("+self.placeholder+","+self.placeholder+")", feature_has_MSMS_precursor_inputValues)
        self.connect.connection.commit()
    
    def fillMascot(self, mascotXMLinstance, runfileroot=None):
        """
        Fill the MASCOT_results table. 

        @type mascotXMLinstance: parseMascot.Reader instance
        @param mascotXMLinstance: Instance of parseMascot.Reader, from which the information will be added to the database
        @param runfileroot: name of the original MS file which should be returned in the MGF title field (optional)
        @raise RuntimeError: There is no database entry with self.msrunName as msrun_name
        @raise RuntimeError: No peptides found
        
        B{Example:}
        
        >>> import parseMascot
        >>> mascotInstance = parseMascot.Reader('mascotResults.xml')          # make a parseMascot.Reader instance
        >>> fillDatabaseInstance = FillDatabase('example')            # make a FillDatabase instance with msrun named example
        >>> with fillDatabase.FillDatabase('exampleSqliteDb.db', 'example', 'example description') as fd:
        ...     fd.fillMsrun()                                           # need to fill the msrun table first
        ...     fd.fillMascot(mascotInstance)                           # fill the database. msrun name is 'example'
        
         B{Example:}
        
        >>> import parseMascot
        >>> mascotInstance = parseMascot.Reader('mascotResults.xml')          # make a parseMascot.Reader instance
        >>> fillDatabaseInstance = FillDatabase('example')            # make a FillDatabase instance with msrun named example
        >>> with fillDatabase.FillDatabase('exampleSqliteDb.db', 'example', 'example description') as fd:
        ...     fd.fillMsrun()                                           # need to fill the msrun table first
        ...     fd.fillMascot(mascotInstance, "msfile1")             # fill the database. msrun name is 'example'. Mascot search includes results from several original files - just upload the ones from msfile1

        """
        # if the msrunName given to FillDatabase() is not in the database, raise runtime error. Because feature table is linked to msrun with a foreign key, msrun HAS to be filled first
        # msrunName can be None, in which case msrunFilled doesn't have to be true, this can be used for fillFeatureMapping and feature_spectrum_linking because these can be done independently of msrun
        if not self.msrunFilled and not self.msrunName == None:
            raise RuntimeError, 'There is no record of: \''+str(self.msrunName)+'\' in the msrun table. Run FillDatabase.fillMsrun() first'
        if self.msrunName == None:
            raise RuntimeError, 'msrunName is set to None (this is also the default). You cannot fill the mascot table if msrunName is None. '

        
        self.connect.cursor.execute("SELECT msrun_id FROM `msrun` WHERE msrun_name = "+self.placeholder+"", (self.msrunName,))
        # getting the msrun_id out of the fetchone(). Fetchone returns a tuple containing one value, want to have that value. Thus the [0]
        msrun_id = self.connect.cursor.fetchone()[0]
        

        # keep track of the amount of assigned peptides that weren't found in the database
        count = 0
        # keep track of the peptides already added
        peptideDict = collections.defaultdict(lambda : collections.defaultdict(list))
        for assignedPeptides in mascotXMLinstance.getAssignedPeptidesMZandRTvalue():
            # TODO first check for filename (fileroot) matching the ms run,(not recorded so need to select on method parameters) 
            if runfileroot !=None and assignedPeptides['fileroot'] != runfileroot :
                continue
                #check self.msrunName matches assignedPeptides['fileroot']
                
            # TODO then check for scannumber. 
            if assignedPeptides['scannumber'] !=None:
                # TODO If scannumber then link directly with that (spectrum ->precursor) after checking rt/mz match  else
                self.connect.cursor.execute("SELECT precursor_id FROM MSMS_precursor "+
                                            "JOIN spectrum ON spectrum_id = spectrum_spectrum_id "+
                                            "AND spectrum_index = "+self.placeholder+" "+
                                            "AND msrun_msrun_id = "+self.placeholder+"", (assignedPeptides['scannumber'], msrun_id))
                result = self.connect.cursor.fetchone()
                if result == None:
                    print 'not found scan number: ',assignedPeptides['scannumber']
                    count += 1
                    continue
            else:
            # TODO cascade to matching spectra vs rt and mz values.

            # because mysql (and hopefully sqlite, otherwise change this for that) rounds to nearest even number when last number is 5, if len after
            # comma is 10 and last number is 5 and second last number is even, make last number 4 (so that python also rounds to nearest even in that case)
            # otherwise python rounds 5 up.
                if len(assignedPeptides['mz'].split('.')[1]) == 10 and assignedPeptides['mz'].endswith('5') and int(assignedPeptides['mz'][-2]) % 2 == 0:
                    assignedPeptides['mz'] = assignedPeptides['mz'][:-1]+'4'
            # round result to 9th digit, do the same for ion_mz. 9 is enough to get unique results, and this way makes sure
            # that not one has more significant numbers and thats why they dont match up
                select_inputValues = (round(float(assignedPeptides['mz']),9), round(float(assignedPeptides['rt']),4), msrun_id)
                self.connect.cursor.execute("SELECT precursor_id FROM MSMS_precursor "+
                                            "JOIN spectrum ON spectrum_id = spectrum_spectrum_id "+
                                            "AND ROUND(ion_mz,9) = "+self.placeholder+" AND ROUND(scan_start_time,4) = "+self.placeholder+" "+
                                            "AND msrun_msrun_id = "+self.placeholder+"", select_inputValues)
                result = self.connect.cursor.fetchone()
                # if the peptide was not found in database, count and continue with next peptide
                if result == None:
                    print 'not found mz:',select_inputValues[0],'scan_start_time: ',select_inputValues[1]
                    count += 1
                    continue

            if not peptideDict['pep_id'].has_key(assignedPeptides['pep_scan_title']) and not assignedPeptides['pep_seq'] in peptideDict[assignedPeptides['pep_scan_title']]['pep_seq_list']:
                # add the info to the mascot table
                # get the primary key

                mascot_primaryKey = self.getPrimaryKeyValue('peptide_id', 'MASCOT_peptide')
                mascot_inputValues = (mascot_primaryKey, assignedPeptides['pep_exp_mz'], assignedPeptides['pep_exp_mr'], assignedPeptides['pep_exp_z']\
                                  ,assignedPeptides['pep_calc_mr'], assignedPeptides['pep_delta'], assignedPeptides['pep_miss'],assignedPeptides['pep_score']\
                                  ,assignedPeptides['pep_expect'], assignedPeptides['pep_res_before'], assignedPeptides['pep_seq'], assignedPeptides['pep_res_after']\
                                  ,assignedPeptides['pep_var_mod'],assignedPeptides['pep_var_mod_pos'],assignedPeptides['pep_num_match'], assignedPeptides['pep_scan_title'],1, result[0])

                self.connect.cursor.execute("INSERT INTO MASCOT_peptide VALUES("+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","\
                                                                            +self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","\
                                                                            +self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","\
                                                                            +self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","\
                                                                            +self.placeholder+","+self.placeholder+")", mascot_inputValues)
                peptideDict[assignedPeptides['pep_scan_title']]['pep_id'] = mascot_primaryKey

                peptideDict[assignedPeptides['pep_scan_title']]['pep_seq_list'].append(assignedPeptides['pep_seq'])
            


                    
            
                
            mascot_protein_primaryKey = self.getPrimaryKeyValue('mascot_protein_id', 'MASCOT_protein')
            mascot_protein_inputValues = (mascot_protein_primaryKey, assignedPeptides['protAccession'], assignedPeptides['prot_desc'], assignedPeptides['prot_score']\
                                          ,assignedPeptides['prot_mass'], assignedPeptides['prot_matches'], assignedPeptides['prot_matches_sig']\
                                          ,assignedPeptides['prot_sequences'], assignedPeptides['prot_sequences_sig'], peptideDict[assignedPeptides['pep_scan_title']]['pep_id'])
            self.connect.cursor.execute("INSERT INTO MASCOT_protein VALUES("+self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","\
                                                                            +self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","\
                                                                            +self.placeholder+","+self.placeholder+")",mascot_protein_inputValues)

            
        if count > 0:
            warnings.warn(str(count)+' assigned peptides not found in database for msrun: '+self.msrunName+'. Make sure fillSpectrum() was called before fillMascot().')

        for unassignedPeptide in mascotXMLinstance.getUnassignedPeptidesMZandRTvalue():
            # because mysql (and hopefully sqlite, otherwise change this for that) rounds to nearest even number when last number is 5, if len after
            # comma is 10 and last number is 5 and second last number is even, make last number 4 (so that python also rounds to nearest even in that case)
            # otherwise python rounds 5 up.
            if len(unassignedPeptide['mz'].split('.')[1]) == 10 and unassignedPeptide['mz'].endswith('5') and int(unassignedPeptide['mz'][-2]) % 2 == 0:
                unassignedPeptide['mz'] = unassignedPeptide['mz'][:-1]+'4'
            # round result to 9th digit, do the same for ion_mz. 9 is enough to get unique results, and this way makes sure
            # that not one has more significant numbers and thats why they dont match up
            select_inputValues = (round(float(unassignedPeptide['mz']),9), round(float(unassignedPeptide['rt']),4), msrun_id)
            self.connect.cursor.execute("SELECT precursor_id FROM MSMS_precursor "+
                                "JOIN spectrum ON spectrum_id = spectrum_spectrum_id "+
                                "AND ROUND(ion_mz,9) = "+self.placeholder+" AND ROUND(scan_start_time,4) = "+self.placeholder+" "+
                                "AND msrun_msrun_id = "+self.placeholder+"", select_inputValues)
            # if the peptide was not found in database, count and continue with next peptide
            result = self.connect.cursor.fetchone()
            if result == None:
                print 'not found mz:',select_inputValues[0],'scan_start_time: ',select_inputValues[1]
                count += 1
                continue
            
            # get the primary key
            mascot_primaryKey = self.getPrimaryKeyValue('peptide_id', 'MASCOT_peptide')
            # add the info to the mascot table
            mascot_inputValues = (mascot_primaryKey, unassignedPeptide['pep_exp_mz'], unassignedPeptide['pep_exp_mr'], unassignedPeptide['pep_exp_z']\
                                  ,unassignedPeptide['pep_calc_mr'], unassignedPeptide['pep_delta'], unassignedPeptide['pep_miss'],unassignedPeptide['pep_score']\
                                  ,unassignedPeptide['pep_expect'], unassignedPeptide['pep_seq']\
                                  ,unassignedPeptide['pep_var_mod'],unassignedPeptide['pep_var_mod_pos'],unassignedPeptide['pep_num_match'],unassignedPeptide['pep_scan_title'],0,result[0])

            self.connect.cursor.execute("INSERT INTO MASCOT_peptide (peptide_id, pep_exp_mz, pep_exp_mr, pep_exp_z, pep_calc_mr, pep_delta, pep_miss, pep_score, pep_expect, pep_seq, pep_var_mod, pep_var_mod_pos, pep_num_match, "\
                                                                  +"pep_scan_title, isAssigned, precursor_precursor_id) VALUES("\
                                                                            +self.placeholder+","+self.placeholder+","+self.placeholder+","\
                                                                            +self.placeholder+","+self.placeholder+","+self.placeholder+","\
                                                                            +self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","\
                                                                            +self.placeholder+","+self.placeholder+","+self.placeholder+","+self.placeholder+","\
                                                                            +self.placeholder+","+self.placeholder+")", mascot_inputValues)        
        if count > 0:
            warnings.warn(str(count)+' assigned peptides not found in database for msrun:'+self.msrunName+'. Make sure fillSpectrum() was called before fillMascot().')
        self.connect.connection.commit()
