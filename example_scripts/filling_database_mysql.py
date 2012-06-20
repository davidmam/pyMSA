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
Example how to fill the database.
"""

# author: ndeklein
# date: 19/04/2012
# summary: Example how to fill the database.


import sys

# for me, PyMSA_dev is not in my default python path
try:
    sys.path.append('/homes/ndeklein/workspace/MS/Trunk/PyMSA_dev')
    sys.path.append('/homes/ndeklein/python2.6/site-packages')
except:
    pass

from pyMSA import database
from pyMSA import parseFeatureXML
from pyMSA import parseMascot
import pysqlite2.dbapi2
import pymzml

import time
import pstats
import cProfile

def main():
    """
    Example how to fill the pyMSA database.
    """
    
    # change the following locations
    jg_c1 = '/homes/dmamartin/Documents/PROTEOMICS/Cantrell/openMS/JG-C1-1.mzML'
    jg_c1a =  '/homes/dmamartin/Documents/PROTEOMICS/Cantrell/openMS/JG-C1-1A.mzML'
    jg_c18 = '/homes/dmamartin/Documents/PROTEOMICS/Cantrell/openMS/JG-C1-18.mzML'
    
    
    # change the following locations
    # '/homes/dmamartin/Documents/PROTEOMICS/Cantrell/openMS/JG-C1-1.raw.i_c1000.featureXML',
    #                    '/homes/dmamartin/Documents/PROTEOMICS/Cantrell/openMS/JG-C1-1.raw.i_c1500.featureXML',
    #                    '/homes/dmamartin/Documents/PROTEOMICS/Cantrell/openMS/JG-C1-1.raw.i_c2000.featureXML',
    featureXML_jg_c1 = ['/homes/ndeklein/Cantrell/featureXML/JG-C1-1.raw.i_c2500.featureXML']
    #                    '/homes/dmamartin/Documents/PROTEOMICS/Cantrell/openMS/JG-C1-1.raw.i_c3000.featureXML',
    #                    '/homes/dmamartin/Documents/PROTEOMICS/Cantrell/openMS/JG-C1-1.raw.i_c3500.featureXML',
    #                    '/homes/dmamartin/Documents/PROTEOMICS/Cantrell/openMS/JG-C1-1.raw.i_c4000.featureXML']
    
    #'/homes/dmamartin/Documents/PROTEOMICS/Cantrell/openMS/JG-C1-1A.raw.i_c1000.featureXML',
     #                   '/homes/dmamartin/Documents/PROTEOMICS/Cantrell/openMS/JG-C1-1A.raw.i_c1500.featureXML',
      #                  '/homes/dmamartin/Documents/PROTEOMICS/Cantrell/openMS/JG-C1-1A.raw.i_c2000.featureXML',
    featureXML_jg_c1a = ['/homes/ndeklein/Cantrell/featureXML/JG-C1-1A.raw.i_c2500.featureXML']
   #                     '/homes/dmamartin/Documents/PROTEOMICS/Cantrell/openMS/JG-C1-1A.raw.i_c3000.featureXML',
   #                     '/homes/dmamartin/Documents/PROTEOMICS/Cantrell/openMS/JG-C1-1A.raw.i_c3500.featureXML',
   #                     '/homes/dmamartin/Documents/PROTEOMICS/Cantrell/openMS/JG-C1-1A.raw.i_c4000.featureXML']

    #'/homes/ndeklein/Cantrell/analysis_old/trafoXML/JG-C1-1__JG-C1-1A.raw.i_c1000__file_1.trafoXML',
    #                  '/homes/ndeklein/Cantrell/analysis_old/trafoXML/JG-C1-1__JG-C1-1A.raw.i_c1500__file_1.trafoXML',
    #                  '/homes/ndeklein/Cantrell/analysis_old/trafoXML/JG-C1-1__JG-C1-1A.raw.i_c2000__file_1.trafoXML',
   # trafoXML_files = ['/homes/ndeklein/Cantrell/analysis_old/trafoXML/JG-C1-1__JG-C1-1A.raw.i_c2500__file_1.trafoXML']
    #                  '/homes/ndeklein/Cantrell/analysis_old/trafoXML/JG-C1-1__JG-C1-1A.raw.i_c3000__file_1.trafoXML',
    #                  '/homes/ndeklein/Cantrell/analysis_old/trafoXML/JG-C1-1__JG-C1-1A.raw.i_c3500__file_1.trafoXML',
    #                  '/homes/ndeklein/Cantrell/analysis_old/trafoXML/JG-C1-1__JG-C1-1A.raw.i_c4000__file_1.trafoXML',]



    with database.ConnectMySQL('gjb-mysql-1.cluster.lifesci.dundee.ac.uk', 'ndeklein', 'm31th3amh4','test') as sqlCon:      
        fillDatabase = database.FillDatabase(sqlCon, 'JG-C1-1')
        time0 = time.time()
        try:
            print 'doing fillMsrun'
            fillDatabase.fillMsrun(jg_c1)
        except pysqlite2.dbapi2.IntegrityError, e:
            print 'msrun was already filled'
            print e
        print 'it took',time.time()-time0,'seconds'
         # mzml instance
        mzmlInstance = pymzml.run.Reader(jg_c1)
        print 'fill spectrum'
        time0 = time.time()
        fillDatabase.fillSpectrum(mzmlInstance)
        print ' It took',time.time()-time0,'seconds\n'
        featureXMLcount = 0                                                                             # fill the msrun table. msrun name is 'example'
        for featureXML_path in featureXML_jg_c1:
            print 'doing feature number:',featureXMLcount+1
            time0 = time.time()
            fillDatabase.fillFeatures(parseFeatureXML.Reader(featureXML_path), intensity_cutoff = float(featureXML_path.split('_c')[1].rstrip('.featureXML')))                                               # fill the other feature tables. 
            print ' It took',time.time()-time0,'seconds\n'
            featureXMLcount += 1
        
        print 'linking spectrum to feature'
        time0 = time.time()
        fillDatabase.linkSpectrumToFeature()
        print 'It took',time.time()-time0,'seconds\n'
        print 'filling mascot'
        time0 = time.time()
        mascot = parseMascot.Reader('/homes/ndeklein/Cantrell/mascot/JG_C1-1_mascot.xml')
        fillDatabase.fillMascot(mascot)
        print 'It took',time.time()-time0,'seconds\n'

    with database.ConnectMySQL('gjb-mysql-1.cluster.lifesci.dundee.ac.uk', 'ndeklein', 'm31th3amh4','test') as sqlCon:   
        fillDatabase = database.FillDatabase(sqlCon, 'JG-C1-1A')    
        time0 = time.time()
        try:
            print 'doing fillMsrun'
            fillDatabase.fillMsrun(jg_c1a)
        except pysqlite2.dbapi2.IntegrityError, e:
            print 'msrun was already filled'
            print e
        print 'it took',time.time()-time0,'seconds'
        # mzml instance
        mzmlInstance = pymzml.run.Reader(jg_c1a)
        print 'doing spectrum'
        time0 = time.time()
        fillDatabase.fillSpectrum(mzmlInstance)
        print ' It took',time.time()-time0,'seconds\n'
        featureXMLcount = 0                                                                             # fill the msrun table. msrun name is 'example'
        for featureXML_path in featureXML_jg_c1a:
            print 'doing feature number:',featureXMLcount+1
            time0 = time.time()
            fillDatabase.fillFeatures(parseFeatureXML.Reader(featureXML_path), intensity_cutoff = float(featureXML_path.split('_c')[1].rstrip('.featureXML')))                                               # fill the other feature tables. 
            print ' It took',time.time()-time0,'seconds\n'
            featureXMLcount += 1 
    
        print 'linking spectrum to feature'
        time0 = time.time()
        fillDatabase.linkSpectrumToFeature()
        print ' It took',time.time()-time0,'seconds\n'
        
        print 'filling mascot'
        time0 = time.time()
        mascot = parseMascot.Reader('/homes/ndeklein/Cantrell/mascot/JG_C1-1A_mascot.xml')
        fillDatabase.fillMascot(mascot)
        print 'It took',time.time()-time0,'seconds\n' 
    
                    
    # give the feature xml files relative to the featureXML count. one file has to be 7 before that (so 1000 corresponds to 1000, 2000 to 2000 etc)
    with database.ConnectMySQL('gjb-mysql-1.cluster.lifesci.dundee.ac.uk', 'ndeklein', 'm31th3amh4','test') as sqlCon:   
        fillDatabase = database.FillDatabase(sqlCon, 'None')
        count = 0
        for index in range(0,8):
            print 'doing featuremapping number:', index+1
            time0 = time.time()
            if index < 7:
                fillDatabase.fillFeatureMapping(parseFeatureXML.Reader(featureXML_jg_c1[index]), parseFeatureXML.Reader(featureXML_jg_c1a[index]), trafoXML_files[index])
#            elif index < 14:
#                fillDatabase.fillFeatureMapping(parseFeatureXML.Reader(featureXML_jg_c1[index-7]), parseFeatureXML.Reader(featureXML_jg_c18[index-7]), trafoXML_files[index])
#            elif index < 21:
#                fillDatabase.fillFeatureMapping(parseFeatureXML.Reader(featureXML_jg_c1a[index-14]), parseFeatureXML.Reader(featureXML_jg_c18[index-14]), trafoXML_files[index])
            print ' It took',time.time()-time0,'seconds\n'



 

if __name__ == '__main__':
    import sys

    # run the profile
    
    cProfile.run('main()', 'profile_filling_database.profile')
    stats = pstats.Stats('profile_filling_database.profile')
    
    # Read all 5 stats files into a single object
    stats.strip_dirs()
    
    # Sort the statistics by the cumulative time spent in the function
    stats.sort_stats('cumulative')
    
    stats.print_stats()
    

