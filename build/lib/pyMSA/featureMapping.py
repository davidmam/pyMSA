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
Maps two feature files to eachother by comparing the trafoXML file and the original featureXML files.  
"""

# author: ndeklein
# date:02/04/2012
# summary: Compares quality of data of two mapped featureXML files.

import parseFeatureXML
from xml.etree import cElementTree
import elementFunctions

class Map():
    """
    FeatureMappingQuality contains functions to compare two mapped featureXML files.     
    
    B{Changes:}
    
    I don't really like how I did this class, it's inconsistent, has some redundancy and difficult to understand. Could use a revamp.   
    """
    def __init__(self,mapped_featureXML_1, mapped_featureXML_2, trafoXML_file):
        """
        @type mapped_featureXML_1: pyMS.pareFeatureXML.Reader
        @param mapped_featureXML_1: An instance of L{parseFeatureXML.Reader}. This is one of the files mapped by OpenMS's MapAlignerPoseClustering.
        @type mapped_featureXML_2: pyMS.pareFeatureXML.Reader
        @param mapped_featureXML_2: An instance of L{parseFeatureXML.Reader}. This is one of the files mapped by OpenMS's MapAlignerPoseClustering.
        @type trafoXML_file: string
        @param trafoXML_file: path to the trafoXML file that corresponds to featureXML instance 1 and featureXML instance 2. Has to be the linear file, because the identity file doesn't contain transformations
        @raise IOError: trafoXML is an identity file (need a linear file)
        @raise RuntimeError: FeatureXML and trafo_xml didn't match up
        """
        # self.retentionDict_1 will contain all the feature info with retention time as key of featureXML file 1
        self.retentionDict_1 = {}
        # self.retentionDict_2 will contain all the feature info with retention time as key of featureXML file 2
        self.retentionDict_2 = {}
        # this method is more expensive on memory, but a lot faster than old method (old method used getWindow, which looped through the list each time)
        # this makes the retention time the key value, so that the retention time can be found with O(1)
        # the retention time is rounded to second point after decimal because that is unique enough
        for feature in mapped_featureXML_1.getSimpleFeatureInfo():
            self.retentionDict_1[str(mapped_featureXML_1['retention time'])] = {'intensity':mapped_featureXML_1.getElementInfo()['intensity'], 'feature_id':mapped_featureXML_1['id']}

        for feature in mapped_featureXML_2.getSimpleFeatureInfo():
            self.retentionDict_2[str(mapped_featureXML_2['retention time'])] = {'intensity':mapped_featureXML_2.getElementInfo()['intensity'], 'feature_id':mapped_featureXML_2['id']}
        # to keep the to and rom changes in a list of dictionairies with as keys 'from' and 'to' and as values the retention times
        self.trafoXML_list = []
        
        for event, element in cElementTree.iterparse(trafoXML_file):
            if element.tag == 'Transformation':
                if elementFunctions.getItems(element)['name'] == 'identity':
                    raise IOError, trafoXML_file+' is a trafoXML identity file (see the Transformation node). There is no information in the identity file. Use the \'linear\' file as input'
            if element.tag == 'Pair':
                try:
                    fromFeatureID = self.retentionDict_1[str(elementFunctions.getItems(element)['from'])]['feature_id']
                except KeyError:
                    pass
                try:
                    toFeatureID = self.retentionDict_1[str((elementFunctions.getItems(element)['to']))]['feature_id']
                except KeyError:
                    pass
                try:
                    fromFeatureID = self.retentionDict_2[str(elementFunctions.getItems(element)['from'])]['feature_id']
                except KeyError:
                    pass
                try:
                    toFeatureID = self.retentionDict_2[str(elementFunctions.getItems(element)['to'])]['feature_id']                
                except KeyError:
                    pass

                try:
                    self.trafoXML_list.append({'from_featureID':fromFeatureID, 'to_featureID':toFeatureID, 'from':float(elementFunctions.getItems(element)['from']), 'to':float(elementFunctions.getItems(element)['to'])})
                except UnboundLocalError, e:
                    raise RuntimeError, 'Something wrong with the input files. Probably the featureXML files didn\'t match the trafoXML file. Check your input. Actual error raised was: '+str(e)
                    
        # bool to know which file is the mapping file and which file is the mapped file (identity file is the mapping file, linear file is the mapped file)
        self.identityFile = None
        # to keep the mapped and non-mapped retention times. This way, if you use unmappedIntensities() and mappedIntensities() it will only run them once
        self.mappingDict = {}
    
    def mapping(self):
        """
        Map the retention times of the two featureXML file to the corresponding trafoXML file. 
       
        @rtype: dict
        @return: Return the retention times of both featureXML_1 and featureXML_2 (those given to __init__) that don't and do map. They are returned in a dict with keys 'featureXML_1_mapped', 'featureXML_1_not_mapped','featureXML_2_mapped' and 'featureXML_2_not_mapped. The values are a list of retention times.
        @attention: This function might b e useless, possibly the same thing is already archieved in the __init__. Have't come around to check this yet to make sure though. 
        
        B{Example:}
        
        >>> import parseFeatureXML
        >>> import featureMapping as fm
        >>> featureXML_1 = parseFeatureXML.Reader('featureXML_example.featureXML')            
        >>> featureXML_2 = parseFeatureXML.Reader('featureXML_example.featureXML')
        >>> featureMapping = fm.FeatureMapping(featureXML_1, featureXML_2, 'trafoXML_example.trafoXML')
        >>> print featureMapping.mapping()
        {'featureXML_1_mapped': set(['4009.59', '5107.29', '5109.29']),'featureXML_1_not_mapped': set(['7052.29']), 'featureXML_2_mapped': set(['3969.59', '5189.29', '5197.29']),'featureXML_2_not_mapped': set(['5345.29'])} 
        
        """
        # featureXML_set_1 and 2 will contain the retention times of the featureXML files 
        featureXML_set_1 = set([])
        featureXML_set_2 = set([])
        # trafo_from_set will contain the retention times of the trafoXML file from the 'from' node
        trafo_from_set = set([])
        # trafo_from_set will contain the retention times of the trafoXML file from the 'to' node
        trafo_to_set = set([])
        
        # add all the retention times to the right set
        for retentionTime in self.retentionDict_1:
            featureXML_set_1.add(retentionTime)
        for retentionTime in self.retentionDict_2:
            featureXML_set_2.add(retentionTime)
        for retentionTime in self.trafoXML_list:
            # because the rt values in featureXML files are rounded to 8 decimals, do the same for trafoxml
            trafo_from_set.add(str(retentionTime['from']))
            trafo_to_set.add(str(retentionTime['to']))

        # if the length of featureXML_set_1 - trafo_to_set is smaller than - trafo from set,
        # use the to_set, otherwise, use the from_set. The correct one will always remove more retention times
        featureXML_set_1_minus_trafo_to_set = featureXML_set_1.difference(trafo_to_set)
        featureXML_set_1_minus_trafo_from_set = featureXML_set_1.difference(trafo_from_set)
        if len(featureXML_set_1_minus_trafo_to_set) < len(featureXML_set_1_minus_trafo_from_set):
            # featureXML_set_1 is the identity
            # featureXML_set_2 is the linear
            self.identityFile = 1
            featureXML_set_1_not_mapped = featureXML_set_1_minus_trafo_to_set
            featureXML_set_1_mapped = featureXML_set_1.intersection(trafo_to_set)
            featureXML_set_2_not_mapped = featureXML_set_2.difference(trafo_from_set)
            featureXML_set_2_mapped = featureXML_set_2.intersection(trafo_from_set)
        elif len(featureXML_set_1_minus_trafo_to_set) > len(featureXML_set_1_minus_trafo_from_set):
            self.identityFile = 2
            # featureXML_set_1 is the linear
            # featureXML_set_2 is the identity
            featureXML_set_1_not_mapped = featureXML_set_1_minus_trafo_from_set
            featureXML_set_1_mapped = featureXML_set_1.intersection(trafo_from_set)
            featureXML_set_2_not_mapped = featureXML_set_2.difference(trafo_to_set)
            featureXML_set_2_mapped = featureXML_set_2.intersection(trafo_to_set)
        else:
            raise RuntimeError, 'Something is wrong with the featureXML files and/or trafoXML files. None of the retention times '\
                                +'of the trafoXML mapped to the the first featureXML instance given. Make sure that the trafoXML file '\
                                +'corresponds to the two featureXML instances given'
       
        self.mappingDict = {'featureXML_1_mapped':featureXML_set_1_mapped, 'featureXML_1_not_mapped':featureXML_set_1_not_mapped, 
                'featureXML_2_mapped':featureXML_set_2_mapped, 'featureXML_2_not_mapped':featureXML_set_2_not_mapped}
        
        self.mapped = True
        return self.mappingDict
    
    def getMappedFeatureIds(self):
        """
        Return self.trafoXML_list. Because this class was such a mess this function used to be redundant, calling self.mapping() when it's not necesarry etc.
        Might be more fixable.
                
        @rtype: list
        @return: Return the mapping feature ids and the mapped feature ids as a list of dictionaries
                                
        B{Example:}
        
        >>> import parseFeatureXML
        >>> import featureMapping as fm
        >>> featureXML_1 = parseFeatureXML.Reader('featureXML_example.featureXML')            
        >>> featureXML_2 = parseFeatureXML.Reader('featureXML_example.featureXML')
        >>> featureMapping = fm.FeatureMapping(featureXML_1, featureXML_2, 'trafoXML_example.trafoXML')
        >>> for feautureID_dict in featureMapping.getMappedFeatureIds():
        ...    print feaureID_dict
        {'from_featureID': 'f_13020522388175237334','to_featureID': 'f_13020522388175237334'}
        {'from_featureID': 'f_43922326584371237334','to_featureID': 'f_43922326584371237334'}
        {'from_featureID': 'f_8613715360396561740', 'to_featureID': 'f_8613715360396561740'} 
        """
        # if mappingDict is empty, mapping has not run for this instance of FeatureMappingQuality yet. Run it.
        #if not self.mappingDict:
        #    self.mapping()
        
        return self.trafoXML_list
    
    def unmappedIntensities(self):
        """
        Get the intensities of the features that weren't mapped.
        
        @rtype: two lists
        @return: Two lists with the intensities of all the features of the first and second featureXML given to FeatureMappingQuality that weren't in the trafoXML file 
        
        B{Example:}
        
        Get the intensities of all the non-mapped features of both featureXML files
        
        >>> import parseFeatureXML
        >>> import featureMapping as fm
        >>> featureXML_1 = parseFeatureXML.Reader('featureXML_example.featureXML')            
        >>> featureXML_2 = parseFeatureXML.Reader('featureXML_example.featureXML')
        >>> featureMapping = fm.FeatureMapping(featureXML_1, featureXML_2, 'trafoXML_example.trafoXML')
        >>> print featureMapping.unmappedIntensities()
        (['556384', '111429', '234284'], ['524284', '111329', '524284'])
        """
        # if mappingDict is empty, mapping has not run for this instance of FeatureMappingQuality yet. Run it.
        if not self.mappingDict:
            self.mapping()

        # the non-mapped values in the first featureXML instance
        featureXML_unmapped_1 = self.mappingDict['featureXML_1_not_mapped']
        # the non-mapped values in the second featureXML instance
        featureXML_unmapped_2 = self.mappingDict['featureXML_2_not_mapped']
        
        # lists to contain the intensities of the unmapped features
        unmappedList_1 = []
        unmappedList_2 = []
        # loop through all the retention times of the non-mapped features and look it up in the retentionDict corresponding
        # that the right number of featureXML instance
        for retentionTime in featureXML_unmapped_1:
            unmappedList_1.append(self.retentionDict_1[retentionTime]['intensity'])
            
        for retentionTime in featureXML_unmapped_2:
            unmappedList_2.append(self.retentionDict_2[retentionTime]['intensity'])
        
        return unmappedList_1, unmappedList_2
        
    
    def mappedIntensities(self):
        """
        Calculate how many features did get mapped and what their intensities are.
        
        @rtype: two lists
        @return: Two lists with the intensities of all the features of the first and second featureXML given to FeatureMappingQuality that were in the trafoXML file 
        
        B{Example:}
        
        Get the intensities of all mapped features of both featureXML files.
        
        >>> import parseFeatureXML
        >>> import featureMapping as fms
        >>> featureXML_1 = parseFeatureXML.Reader('featureXML_example.featureXML')            
        >>> featureXML_2 = parseFeatureXML.Reader('featureXML_example.featureXML')
        >>> featureMappingQuality = fm.FeatureMapping(featureXML_1, featureXML_2, 'trafoXML_example.trafoXML')
        >>> print featureMapping.mappedIntensities()
        (['52234'], ['524284'])
        """
        # if mappingDict is empty, mapping has not run for this instance of FeatureMappingQuality yet. Run it.
        if not self.mappingDict:
            self.mapping()
            
        # the non-mapped values in the first featureXML instance
        featureXML_mapped_1 = self.mappingDict['featureXML_1_mapped']
        # the non-mapped values in the second featureXML instance
        featureXML_mapped_2 = self.mappingDict['featureXML_2_mapped']
        
        # lists to contain the intensities of the unmapped features
        mappedList_1 = []
        mappedList_2 = []
        # loop through all the retention times of the non-mapped features and look it up in the retentionDict corresponding
        # that the right number of featureXML instance
        for retentionTime in featureXML_mapped_1:
            mappedList_1.append(self.retentionDict_1[retentionTime]['intensity'])
        for retentionTime in featureXML_mapped_2:
            mappedList_2.append(self.retentionDict_2[retentionTime]['intensity'])
        
        return mappedList_1, mappedList_2