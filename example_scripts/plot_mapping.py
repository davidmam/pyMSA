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
Example how to plot the amount of mapped features. Works only when pyMS_database.db has been filled, including at least msrun, feature and feature_mapping. 
"""

# author: ndeklein
# date:26/04/2012
# summary: Example how to plot the amount of mapped features. Works only when pyMS_database.db has been filled, including at least msrun, feature and feature_mapping. 

import sys

# for me, PyMSA_dev is not in my default python path
try:
    sys.path.append('/homes/ndeklein/workspace/MS/Trunk/PyMSA_dev')
except:
    pass


from pyMSA import database
from pyMSA import rPlotGenerics
import rpy2.robjects as R


def plotMappingPerIntensity():
    """
    Plots the amount of features mapped per intensity cut-off.
    
    B{Example:}
    
    <todo>
    """

    # to be able to set ylim and xlim correctly
    yMax = 0
    xMax = 0   
    msrunResult = []

    # open the png
    R.r.png('example_files/output/mapped_feature_per_intensity_allthree.png', width=600, height=600)
    
 
    # make a connection to the default database (database/pyMSA_databasee.db)
    with database.ConnectSqlite(databaseName='../database/pyMSA_database.db') as iwd:
        # for the legends
        legenddNames = []
        # select the max id in msrun
        iwd.cursor.execute("SELECT MAX(msrun_id) FROM msrun")
        idList = range(1, iwd.cursor.fetchone()[0]+1)
        # loop from 1 till the max id. iwd.fetchone() returns a tuple with one value, get value from the tuple with [0].
        i = 0 
        for id in idList:
            i += 1
            # quick and dirty solution to loop over all numbers. now its 1-1, 1-2, 1-3, 2-1, 2-2, 2-3, 3-1, 3-2,3-3, could be done better (but for now
            # need it because 1-2 and 2-1 has to be checked to get both identity and mapping
            for id2 in idList[i:]:
                # bool to see if id and id2 find something
                nothingFound = False
                # we don't need to compare 1 with 1 and 2 with 2 etc so if id and id2 is the same, continue
                if int(id) == int(id2):
                    continue
                iwd.cursor.execute("SELECT msrun_name FROM msrun WHERE msrun_id = ?",(id,))
                feature_got_mapped_id = iwd.cursor.fetchone()[0]
                iwd.cursor.execute("SELECT msrun_name FROM msrun WHERE msrun_id = ?",(id2,))
                feature_identity_id = iwd.cursor.fetchone()[0]
                mappedName = str(feature_got_mapped_id)+' mapped to '+str(feature_identity_id)
                legenddNames.append(mappedName)
                # List to keep track of the amount of mapping per intensity
                mappingList = []
                # List for the intensity cut-off.
                intensityCutoffList = []
                #  loop for every distinct intenstiy cut-off through
                iwd.cursor.execute("SELECT DISTINCT(intensity_cutoff) FROM feature WHERE msrun_msrun_id = ?", (id,))
                for intensity in iwd.cursor.fetchall():
                    # selects the count of the amount of features per id in table msrun with each other id in table msrun
                    iwd.cursor.execute("SELECT COUNT(feature_mapping_id) "+
                                       "FROM feature_mapping JOIN feature ON feature_got_mapped_id = feature_table_id "+
                                       "WHERE intensity_cutoff = ? "+
                                       "AND msrun_msrun_id = ? "+
                                       "AND (SELECT msrun_msrun_id FROM feature WHERE feature_table_id = feature_identity_id) = ?", (intensity[0], id, id2))
                    featureCount = iwd.cursor.fetchone()[0]
                    # if featureCount == 0 it can be that the id2 was mapped to the id instead of other way around, test this
                    if featureCount == 0:
                        iwd.cursor.execute("SELECT COUNT(feature_mapping_id) "+
                                           "FROM feature_mapping JOIN feature ON feature_identity_id = feature_table_id "+
                                           "WHERE intensity_cutoff = ? "+
                                           "AND msrun_msrun_id = ? "+
                                           "AND (SELECT msrun_msrun_id FROM feature WHERE feature_table_id = feature_got_mapped_id) = ?", (intensity[0], id, id2))
                        featureCount = iwd.cursor.fetchone()[0]
                    mappingList.append(featureCount)
                    intensityCutoffList.append(intensity[0])
                
                # if every value in the list is 0, don't append it
                if not sum(mappingList) == 0:    
                    # make the mapping list into a vector
                    mappingVector = R.IntVector(mappingList)
                    # make the intensities in a vector to use for the x-axis
                    intensityVector = R.StrVector(intensityCutoffList)            
                    
                     
                    if max(mappingList) > yMax:
                        yMax = max(mappingList)
                    if max(intensityCutoffList) > xMax:
                        xMax = max(intensityCutoffList)
            
                    msrunResult.append((intensityVector, mappingVector))    

    for index, data in enumerate(msrunResult):
        if index == 0:
            R.r['plot'](data[0], data[1], xlim=R.IntVector((0,xMax)), ylim=R.IntVector((0,yMax)), main='Mapped features per intensity', xlab='intensity cut-off', ylab='# of mapped features', col='red')
        elif index == 1:
            R.r['points'](data[0], data[1], col='blue')
        else:
            R.r['points'](data[0], data[1], col='black')
            
    R.r['legend'](x='topright', legend=R.StrVector((legenddNames[0], legenddNames[1], legenddNames[2])), col=R.StrVector(('red','blue', 'black')), pch=1)
    
    R.r['dev.off']()
         
def plotTotalFeaturesPerIntensity():

    # open the png
    R.r.png('example_files/output/total_features_and_mapping_per_intensity_allthree.png', width=600, height=600)
    
    # to be able to set ylim and xlim correctly
    yMax = 0
    xMax = 0   
    featurePerIntensityResult = []
    featureMappingResult = []
    # make a connection to the default database (database/pyMSA_databasee.db)
    i = 0
    with database.InteractWithDatabase(databaseName='../database/pyMSA_database.db') as iwd:
        # for legends
        msrunNames = []
        legenddNames = []
        # select the max id in msrun
        iwd.cursor.execute("SELECT MAX(msrun_id) FROM msrun")
        idList = range(1, iwd.cursor.fetchone()[0]+1)
        # loop from 1 till the max id. iwd.fetchone() returns a tuple with one value, get value from the tuple with [0]. 
        for id in idList:
            # get the msrun name
            iwd.cursor.execute("SELECT msrun_name FROM msrun WHERE msrun_id = ?", (id,))
            msrunName = iwd.cursor.fetchone()[0]
            
            # get the msrun start time
            iwd.cursor.execute("SELECT start_time FROM msrun WHERE msrun_id = ?", (id,))
            start_time = iwd.cursor.fetchone()[0]
            msrunNames.append(str(msrunName)+'  -  '+str(start_time))
            featureList = []
            intensityCutoffList = []
            #  loop for every distinct intenstiy cut-off through
            iwd.cursor.execute("SELECT DISTINCT(intensity_cutoff) FROM feature WHERE msrun_msrun_id = ?", (id,))
            for intensity in iwd.cursor.fetchall():
                iwd.cursor.execute("SELECT COUNT(feature_id) "+
                                   "FROM feature WHERE msrun_msrun_id = ? "+
                                   "AND intensity_cutoff = ? ", (id,intensity[0]))
                
                featureCount = iwd.cursor.fetchone()[0]
                    
                featureList.append(featureCount)
                intensityCutoffList.append(intensity[0])
            
            # make the mapping list into a vector
            featureVector = R.IntVector(featureList)
            # make the intensities in a vector to use for the x-axis
            intensityVector = R.StrVector(intensityCutoffList)    
            if max(featureList) > yMax:
                yMax = max(featureList)
            if max(intensityCutoffList) > xMax:
                xMax = max(intensityCutoffList)
            
            featurePerIntensityResult.append((intensityVector, featureVector))  
            
            
            
            ####                                                       ###
            #### THIS PART DOES THE FEATUREMAPPING STUFF FOR THE GRAPH ###
            ####                                                       ###
            i += 1
            # quick and dirty solution to loop over all numbers. now its 1-1, 1-2, 1-3, 2-1, 2-2, 2-3, 3-1, 3-2,3-3, could be done better (but for now
            # need it because 1-2 and 2-1 has to be checked to get both identity and mapping
            for id2 in idList[i:]:
                # bool to see if id and id2 find something
                nothingFound = False
                # we don't need to compare 1 with 1 and 2 with 2 etc so if id and id2 is the same, continue
                if int(id) == int(id2):
                    continue
                iwd.cursor.execute("SELECT msrun_name FROM msrun WHERE msrun_id = ?",(id,))
                feature_got_mapped_id = iwd.cursor.fetchone()[0]
                iwd.cursor.execute("SELECT msrun_name FROM msrun WHERE msrun_id = ?",(id2,))
                feature_identity_id = iwd.cursor.fetchone()[0]
                mappedName = str(feature_got_mapped_id)+' mapped to '+str(feature_identity_id)
                legenddNames.append(mappedName)
                # List to keep track of the amount of mapping per intensity
                mappingList = []
                # List for the intensity cut-off.
                intensityCutoffList = []
                #  loop for every distinct intenstiy cut-off through
                iwd.cursor.execute("SELECT DISTINCT(intensity_cutoff) FROM feature WHERE msrun_msrun_id = ?", (id,))
                for intensity in iwd.cursor.fetchall():
                    # selects the count of the amount of features per id in table msrun with each other id in table msrun
                    iwd.cursor.execute("SELECT COUNT(feature_mapping_id) "+
                                       "FROM feature_mapping JOIN feature ON feature_got_mapped_id = feature_table_id "+
                                       "WHERE intensity_cutoff = ? "+
                                       "AND msrun_msrun_id = ? "+
                                       "AND (SELECT msrun_msrun_id FROM feature WHERE feature_table_id = feature_identity_id) = ?", (intensity[0], id, id2))
                    mappingCount = iwd.cursor.fetchone()[0]
                    # if featureCount == 0 it can be that the id2 was mapped to the id instead of other way around, test this
                    if mappingCount == 0:
                        iwd.cursor.execute("SELECT COUNT(feature_mapping_id) "+
                                           "FROM feature_mapping JOIN feature ON feature_identity_id = feature_table_id "+
                                           "WHERE intensity_cutoff = ? "+
                                           "AND msrun_msrun_id = ? "+
                                           "AND (SELECT msrun_msrun_id FROM feature WHERE feature_table_id = feature_got_mapped_id) = ?", (intensity[0], id, id2))
                        mappingCount = iwd.cursor.fetchone()[0]
                    
                    mappingList.append(mappingCount)
                    intensityCutoffList.append(intensity[0])
                
                # if every value in the list is 0, don't append it
                if not sum(mappingList) == 0:    
                    # make the mapping list into a vector
                    mappingVector = R.IntVector(mappingList)
                    # make the intensities in a vector to use for the x-axis
                    intensityVector = R.StrVector(intensityCutoffList)
            
                    featureMappingResult.append((intensityVector, mappingVector))    

    colorList = ['red', 'blue', 'black', 'magenta', 'green', 'purple']
    for index, data in enumerate(featurePerIntensityResult):
        if index == 0:
            R.r['plot'](data[0], data[1], xlim=R.IntVector((950, xMax)), ylim=R.IntVector((0,yMax)), main='Total features per intensity', xlab='intensity cut-off', ylab='# of features', col=colorList[index])
        elif index == 1:
            R.r['points'](data[0], data[1], col=colorList[index])
        else:
            R.r['points'](data[0], data[1], col=colorList[index])
            
    for index, data in enumerate(featureMappingResult):
        R.r['points'](data[0], data[1], col=colorList[index+3], pch=1)
        
    R.r['legend'](x='topright', legend=R.StrVector((msrunNames[0], msrunNames[1], msrunNames[2], legenddNames[0], legenddNames[1], legenddNames[2])), col=R.StrVector(colorList), pch=R.IntVector((1,1,1,4,4,4)))


    R.r['dev.off']()      
  


def plotMsmsPerIntensity():
    # open the png
    R.r.png('example_files/output/total_MSMS_per_intensity_allthree.png', width=600, height=600)
    # to be able to set ylim and xlim correctly
    yMax = 0
    xMax = 0   
    msrunResult = []
    with database.InteractWithDatabase(databaseName='../database/pyMSA_database.db') as iwd:
        # for legend
        msrunNames = []
        # select the max id in msrun
        iwd.cursor.execute("SELECT MAX(msrun_id) FROM msrun")
        # loop from 1 till the max id. iwd.fetchone() returns a tuple with one value, get value from the tuple with [0]. 
        for id in range(1, iwd.cursor.fetchone()[0]+1):
            iwd.cursor.execute("SELECT msrun_name FROM msrun WHERE msrun_id = ?",(id,))
            msrunNames.append(iwd.cursor.fetchone())
            spectrumList = []
            intensityCutoffList = []
            #  loop for every distinct intenstiy cut-off through
            iwd.cursor.execute("SELECT DISTINCT(intensity_cutoff) FROM feature WHERE msrun_msrun_id = ?", (id,))
            for intensity in iwd.cursor.fetchall():
                iwd.cursor.execute("SELECT COUNT(MSMS_precursor_precursor_id) "+ 
                                   "FROM feature_has_MSMS_precursor AS fmp "+
                                   "JOIN feature AS f ON fmp.feature_feature_table_id = f.feature_table_id "+
                                   "AND f.msrun_msrun_id = ? "+
                                   "AND intensity_cutoff = ?",(id, intensity[0]))

                spectrumCount = iwd.cursor.fetchone()[0]
                    
                spectrumList.append(spectrumCount)
                intensityCutoffList.append(intensity[0])
            
            # make the mapping list into a vector
            spectrumVector = R.IntVector(spectrumList)
            # make the intensities in a vector to use for the x-axis
            intensityVector = R.StrVector(intensityCutoffList)             
            
            if max(spectrumList) > yMax:
                yMax = max(spectrumList)
            if max(intensityCutoffList) > xMax:
                xMax = max(intensityCutoffList)
            
            msrunResult.append((intensityVector, spectrumVector)) 

    for index, data in enumerate(msrunResult):
        if index == 0:
            R.r['plot'](data[0], data[1], xlim=R.IntVector((0, xMax)), ylim=R.IntVector((0,yMax)), main='Total MS/MS spectrum that map to a feature per intensity', xlab='intensity cut-off', ylab='# MS/MS spectrum mapped to features', col='red')
        elif index == 1:
            R.r['points'](data[0], data[1], col='blue')
        else:
            R.r['points'](data[0], data[1], col='black')
    R.r['legend'](x='topright', legend=R.StrVector((msrunNames[0], msrunNames[1], msrunNames[2])), col=R.StrVector(('red','blue', 'black')), pch=1)


    R.r['dev.off']()      

def plotFeatureWithoutSpectraPerIntensity():
    # open the png
    R.r.png('example_files/output/total_feature_without_spectra_per_intensity_allthree.png', width=600, height=600)
    # to be able to set ylim and xlim correctly
    yMax = 0
    xMax = 0   
    msrunResult = []
    with database.InteractWithDatabase(databaseName='../database/pyMSA_database.db') as iwd:
        # for legend
        msrunNames = []
        # select the max id in msrun
        iwd.cursor.execute("SELECT MAX(msrun_id) FROM msrun")
        # loop from 1 till the max id. iwd.fetchone() returns a tuple with one value, get value from the tuple with [0]. 
        for id in range(1, iwd.cursor.fetchone()[0]+1):
            iwd.cursor.execute("SELECT msrun_name FROM msrun WHERE msrun_id = ?", (id,))
            msrunNames.append(iwd.cursor.fetchone())
            featureList = []
            intensityCutoffList = []
            #  loop for every distinct intenstiy cut-off through
            iwd.cursor.execute("SELECT DISTINCT(intensity_cutoff) FROM feature WHERE msrun_msrun_id = ?", (id,))
            for intensity in iwd.cursor.fetchall():
                iwd.cursor.execute("SELECT COUNT(feature_table_id) FROM feature "+
                                   "WHERE msrun_msrun_id = ? "+
                                   "AND intensity_cutoff = ?",(id, intensity[0]))

                featureCount = iwd.cursor.fetchone()[0]
                iwd.cursor.execute("SELECT COUNT(MSMS_precursor_precursor_id) "+
                                    "FROM feature_has_MSMS_precursor AS fmp "+
                                    "JOIN MSMS_precursor AS mp ON fmp.MSMS_precursor_precursor_id = mp.precursor_id "+
                                    "JOIN feature ON fmp.feature_feature_table_id = feature.feature_table_id "+
                                    "WHERE feature.msrun_msrun_id = ? "+
                                    "AND intensity_cutoff = ? ",(id, intensity[0]))
                featureWoSpectrum = int(featureCount) - int(iwd.cursor.fetchone()[0])
                featureList.append(featureWoSpectrum)
                intensityCutoffList.append(intensity[0])
            
            # make the mapping list into a vector
            featureVector = R.IntVector(featureList)
            # make the intensities in a vector to use for the x-axis
            intensityVector = R.StrVector(intensityCutoffList)             
            
            if max(featureList) > yMax:
                yMax = max(featureList)
            if max(intensityCutoffList) > xMax:
                xMax = max(intensityCutoffList)
            
            msrunResult.append((intensityVector, featureVector)) 

    for index, data in enumerate(msrunResult):
        if index == 0:
            R.r['plot'](data[0], data[1], xlim=R.IntVector((0, xMax)), ylim=R.IntVector((0,yMax)), main='Total feature that don\'t have a mapped spectrum per intensity', xlab='intensity cut-off', ylab='# feature without spectrum', col='red')
        elif index == 1:
            R.r['points'](data[0], data[1], col='blue')
        else:
            R.r['points'](data[0], data[1], col='black')
    R.r['legend'](x='topright', legend=R.StrVector((msrunNames[0], msrunNames[1], msrunNames[2])), col=R.StrVector(('red','blue', 'black')), pch=1)


    R.r['dev.off']()  



def plotMSMSperFeatureIntensity():
     # open the png
    R.r.png('example_files/output/total_MSMS_per_feature_per_intensity_allthree.png', width=600, height=600)
    # to be able to set ylim and xlim correctly
    yMax = 0
    xMax = 0   
    msrunResult = []
    with database.InteractWithDatabase(databaseName='../database/pyMSA_database.db') as iwd:
        # for legend
        msrunNames = []
        # select the max id in msrun
        iwd.cursor.execute("SELECT MAX(msrun_id) FROM msrun")
        # loop from 1 till the max id. iwd.fetchone() returns a tuple with one value, get value from the tuple with [0]. 
        for id in range(1, iwd.cursor.fetchone()[0]+1):
            iwd.cursor.execute("SELECT msrun_name FROM msrun WHERE msrun_id = ?", (id,))
            msrunNames.append(iwd.cursor.fetchone())
            spectrumList = []
            intensityCutoffList = []
            #  loop for every distinct intenstiy cut-off through
            iwd.cursor.execute("SELECT DISTINCT(intensity_cutoff) FROM feature WHERE msrun_msrun_id = ?", (id,))
            for intensity in iwd.cursor.fetchall():
                iwd.cursor.execute("SELECT COUNT(MSMS_precursor_precursor_id) "+
                                   "FROM feature_has_MSMS_precursor AS fmp "+
                                   "JOIN MSMS_precursor AS mp ON fmp.MSMS_precursor_precursor_id = mp.precursor_id "+
                                   "JOIN feature ON fmp.feature_feature_table_id = feature.feature_table_id "+
                                   "AND feature.msrun_msrun_id = ? "+
                                   "AND intensity_cutoff = ?",(id, intensity[0]))

                spectrumCount = iwd.cursor.fetchone()[0]
                    
                spectrumList.append(spectrumCount)
                intensityCutoffList.append(intensity[0])
            
            # make the mapping list into a vector
            spectrumVector = R.IntVector(spectrumList)
            # make the intensities in a vector to use for the x-axis
            intensityVector = R.StrVector(intensityCutoffList)             
            
            if max(spectrumList) > yMax:
                yMax = max(spectrumList)
            if max(intensityCutoffList) > xMax:
                xMax = max(intensityCutoffList)
            
            msrunResult.append((intensityVector, spectrumVector)) 

    for index, data in enumerate(msrunResult):
        if index == 0:
            R.r['plot'](data[0], data[1], xlim=R.IntVector((0, xMax)), ylim=R.IntVector((0,yMax)), main='Total MS/MS spectrum that map to a feature per intensity', xlab='intensity cut-off', ylab='# MS/MS spectrum mapped to features', col='red')
        elif index == 1:
            R.r['points'](data[0], data[1], col='blue')
        else:
            R.r['points'](data[0], data[1], col='black')
    R.r['legend'](x='topright', legend=R.StrVector((msrunNames[0], msrunNames[1], msrunNames[2])), col=R.StrVector(('red','blue', 'black')), pch=1)


    R.r['dev.off']()

   
plotMappingPerIntensity()
plotTotalFeaturesPerIntensity()
plotMsmsPerIntensity()
plotFeatureWithoutSpectraPerIntensity()
plotMSMSperFeatureIntensity()