# Copyright (c) 2012 - D.M.A.Martin
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
Parser to extract relevant data from a .featureXML file.
"""

# author: dmamartin
# date:20/12/2012
# summary: Parses a consensusXML file. Makes an iterator object out of the parsing (using yield, not __iter__ and __next__).

from xml.etree import cElementTree
import fileHandling
import collections
import elementFunctions

class Reader():
    """
    Generator object with functions to acces information from consensusXML files easily. 
    Reader() applies a __getitem__ function so information can be retrieved from the feature elements
    using the dictionary [key] syntax. 
    
    B{Example}
    
    Print feature id and intensity example with example output:
    
    >>> consensusXML = Reader('example_feature_file.consensusXML')   # make a Reader instance
    >>> elementGroups = consensusXML.getSimpleGroupInfo()                    # get all the features of the Reader instance
    >>> for group in elementGroups:                               # loop through all the features
    ...     print 'intensity of', consensusXML['id'],' = ', consensusXML['intensity']    # print the id and intensity of the feature
    intensity of e_13020522388175237334  =  524284
    intensity of e_8613715360396561740  =  111329
    intensity of e_43922326584371237334  =  524284
    
    B{<TODO>:}
    
    Do something about the minute-second interchangability between peaks, features and spectra (one xml format uses seconds, the other uses minutes)
        
    B{To change (?):} 
 
    The class is a bit weirdly designed, because it has both the generator functions and the __getitem__ function you need to loop through the
    spectra but then use the Reader instance to get the item (see the example, for feature in features: featureXML['id']). This can be changed
    by having a different class called feature which has a __getitem__ function, and yield the feature from the Reader instance.
    However, this method I{does} work, so it is not high on priority (unless it causes a lot of confusion with the user). Same goes for L{parsePeaksMzML.Reader}.
    """
    
    
    # initializer, takes a file path as input
    def __init__(self, path):
        """
        Initialize the Reader instance and check if the file is a valid featureXML file and put it in a fileHandling.FileHandle instance.
        
        @type path: string
        @param path: The path of the feature XML file                       

        """
        # filepath
        self.path = path
        # if the file at path does not start with <?xml, raise an exception that the xml file is invalid
        file = fileHandling.FileHandle(self.path)
        file.isXML()
        # if the first non '<?xml' line of the file does not start with <consensusXML, raise an exception that the file is not a featureXML file 
        file.isConsensusXML() 

        # a flag to see if simpleFeatureInfo or allFeatureInfo is used. This makes a difference in the __getItem__ function
        self.simpleFlag = True
        
        # the current element
        self.element = None
        # a list of all the keys that can be used for __getItem__
        self.__elementKeySet = set([])
        # element dictionary to contain all the elements
        # uses collections.defaultidct to enable unknown keys to be added to the dictionary 
        self.elementInfo = collections.defaultdict(dict)

        # add the keys to _elementKeySet that __getitem__ takes
        self.__elementKeySet.add('intensity')
        self.__elementKeySet.add('mz')
        self.__elementKeySet.add('rt')      
        self.__elementKeySet.add('quality')
        self.__elementKeySet.add('charge')
        self.__elementKeySet.add('elements')
        self.__elementKeySet.add('id')

        self.maplist=[]

        return
    
    # Make an iterable function (by using yield) that returns every element in the file
    def getAllElements(self):
        """
        Iterator function that yields all the elements in the file given to Reader()
        
        @rtype: Element
        @return: Iterator of all the elements in the file
        @raise RuntimeError: No elements in the file

        B{Example}:

        Printing all elements in a file:
        
        >>> consensusXML = Reader('example_consensus_file.consensusXML')    # make a read instance
        >>> allElements = consensusXML.getAllElements()    # get all elements of the reader instance, you can now iterate over allElements
        >>> for element in allElements:
        ...    print element
        <Element 'software' at 0x166a05a0>
        <Element 'processingAction' at 0x166a0600>
        <Element 'feature' at 0x6184270>
        
        """
        inFile = open(self.path)
        
        # counter to keep track of the amount of elements. If it is 0 at the end, a runtime error is raise
        elementCount = 0
        # For every element in the file
        for event, element in cElementTree.iterparse(inFile):
            elementCount += 1
            self.element = element
            # clearing elementInfo to safe memory space
            self.elementInfo.clear()
            yield element
        element.clear()
        # when doing -> for i in readerInstance.getElement, the last loop goes to file.close()
        inFile.close()
        
        # this should never be able to happen because of file.isXML and file.isFeatureXML in the __init__
        if elementCount == 0:
            raise RuntimeError, 'No elements found at getAllElements(), invalid featureXML file: '+str(self.path)

    def getMapInfo(self):
        """Retrieves and stores the map details for files"""

        for element in self.getAllElements():
            if element.tag=='map':
                mapDict={}
                mapid=int(elementFunctions.getItems(element)['id'])
                mapDict['name']=elementFunctions.getItems(element)['name']
                mapDict['unique_id']=elementFunctions.getItems(element)['unique_id']
                mapDict['label' ]=elementFunctions.getItems(element)['label']
                mapDict['size' ]=int(elementFunctions.getItems(element)['size'])
                while len(self.maplist) <=mapid: 
                    self.maplist.append({})
                self.maplist[mapid]=mapDict

        return self.maplist

    # Get the items from getElements, only yield the feature elements
    # Add extra feature specific info to self.elementInfo
    def getSimpleElementInfo(self):
        """
        Iterator function that yields all the feature elements in the file given to Reader().
        It saves info from the features in a dict, self.elementInfo, which is used in the L{parseConsensusXML.Reader.__getitem__} retrieval function.
        This function has predefined information like intensity, overallquality, convexhull etc that make for easier browsing, but because of this
        it does not contain all information. If you want to get all information exactly as found in the xml file, use L{parseConsensusXML.Reader.getAllElementInfo}.        
        
        @rtype: Element
        @return: Iterator of all the elements in the file where element.tag == 'consensusElement'
        @raise RuntimeError: No features in the file
        
        B{Example}:
        
        Printing all the groupedElements in a file:
        
        >>> consensusXML = Reader('example_consensus_file.consensusXML')    # make a reader instance
        >>> allElements = consensusXML.getAllElements()    # get all feature elements of the reader instance, you can now iterate over allElements
        >>> elements = consensusXML.getSimpleElementInfo()
        >>> for element in elements::
        ...    print element
        <Element 'consensusElement' at 0x6184270>
        <Element 'consensusElement' at 0x6184cc0>
        <Element 'consensusElement' at 0x6188630>

        Printing the intensities of all elements:
        
        >>> consensusXML = Reader('example_consensus_file.consensusXML')    # make a reader instance
        >>> allElements = consensusXML.getAllElements()    # get all feature elements of the reader instance, you can now iterate over allElements
        >>> elements = consensusXML.getSimpleElementInfo()
        >>> for element in elements:
        ...    print consensusXML['intensity']
        6182
        3543
        2134
        """
        # counter for the amount of elements with a consensusElement tag. If it stay 0 at the end of the yielding this function raises a runtime error
        elementCount = 0

        # for all the elements
        for element in self.getAllElements():

            if element.tag == 'consensusElement':
                elementCount += 1 # keeping track of the amount of features
                # Add all the necessary keys for easy browsing (so the element name) to elementInfo[element]. This is not very generic
                # but it has all the node names and the features should be easily browsable using the __getitem__ implementation
                # The keys are intensity, overallquality, userParm, convexhull, position, quality, charge
                # This only works as long as the featureXML format stays the same
                self.elementInfo[element]['mz'] = 0
                self.elementInfo[element]['rt'] = 0
                self.elementInfo[element]['intensity'] = 0
                
                self.elementInfo[element]['quality'] = elementFunctions.getItems(element)['quality']
                self.elementInfo[element]['charge'] = elementFunctions.getItems(element)['charge']
                self.elementInfo[element]['elements'] = []
                self.elementInfo[element]['id'] = elementFunctions.getItems(element)['id']
                
                                
                 
                # for every element in feature (the rest of the info of feature is already saved in getAllElements())
                for nestedElement in element:
                    # the mz and retention time is saved in the position (in a very unhandy way) get it out and put it in elementInfo
                    if nestedElement.tag == 'centroid':
                         self.elementInfo[element]['rt'] = float(elementFunctions.getItems(nestedElement)['rt']
)
                         self.elementInfo[element]['mz'] = float(elementFunctions.getItems(nestedElement)['mz'])
                         self.elementInfo[element]['intensity'] = float(elementFunctions.getItems(nestedElement)['it'])

                        
                            #raise RuntimeError, 'Could not retrieve centroid position or intensity.' 
                    
                    # dict to contain the different user params
                    userParamDict = {}
                    # for every key in the element
                    #for key in nestedElement.keys():
                        # to directly access all properties of feature, the name of property is taken as dictionary key
                        # and the result is taken as value.
                     #   userParamDict[key] = elementFunctions.getItems(nestedElement)[key]
                    
                    # Add the info of all the elements in feature to elementInfo
                    if nestedElement.tag == 'groupedElementList':
                        
                        for ele in nestedElement:
                            if ele.tag=='element':
                                eleDict={}
                                if elementFunctions.getItems(ele)['id'][0:2] == 'f_':
                                    
                                    eleDict['id']=elementFunctions.getItems(ele)['id']
                                else:
                                    eleDict['id']='f_%s'%elementFunctions.getItems(ele)['id']
                                
                                self.elementInfo[element]['elements'].append(eleDict)


                        
                yield element
                # this gets called after every yield statement and clears every element that is under the current element. Because all the 
                # nested elements of the current element have already been used and the results saved in self.elementInfo, they are not
                # necessary anymore and clearing them lowers the memory usage. 
                for nestedElement in element:
                    nestedElement.clear()
                element.clear()

        if elementCount == 0:
            raise RuntimeError, 'There were no consensus features found in self.getAllElements(). Not a valid featureXML file:'+str(self.path)


    # Get the items from getElements, only yield the feature elements
    # Add extra feature specific info to self.elementInfo
    def getAllFeatureInfo(self):
        """
        Iterator function that yields all the feature elements in the file given to Reader().
        It saves info from the features in a dict, self.elementInfo, which is used in the L{parseFeatureXML.Reader.__getitem__} retrieval function.
        This function gets all the information from a feature element and does no processing. Because of this the key names are not very intuitive.
        If you want a more intuitive key-name system, use L{parseFeatureXML.Reader.getSimpleFeatureInfo}. That comes at the cost of loss of information though. 
    
        @rtype: Element
        @return: Iterator of all the elements in the file where element.tag == 'feature'
        @raise RuntimeError: No features in the file
        
        B{Example}:
        
        Printing all the features in a file:
        
        >>> featureXML = Reader('example_feature_file.featureXML')    # make a reader instance
        >>> allElements = featureXML.getAllElements()    # get all feature elements of the reader instance, you can now iterate over allElements
        >>> features = featureXML.getAllFeatureInfo()
        >>> for feature in features:                                    # loop through all the features
            print featureXML['nestedElement']
        [{'content': '7052.29224', 'dim': '0', 'tagName': 'position'}, {'content': '322.251104824796', 'dim': '1', 'tagName': 'position'}, {'content': '52234', 'tagName': 'intensity'}, {'content': '0', 'dim': '0', 'tagName': 'quality'}, {'content': '0', 'dim': '1', 'tagName': 'quality'}, {'content': '225053', 'tagName': 'overallquality'}, {'content': '2', 'tagName': 'charge'}, {'nr': '0', 'nestedElement': [{'y': '336.125209180674', 'x': '7052.29224', 'tagName': 'pt'}, {'y': '336.124751115092', 'x': '7052.29224', 'tagName': 'pt'}, {'y': '336.124841989895', 'x': '7052.29224', 'tagName': 'pt'}, {'y': '336.12529301464', 'x': '7052.29224', 'tagName': 'pt'}, {'y': '336.124957942644', 'x': '7052.29224', 'tagName': 'pt'}, {'y': '338.251041063348', 'x': '7052.29224', 'tagName': 'pt'}, {'y': '338.251376135343', 'x': '7052.29224', 'tagName': 'pt'}, {'y': '338.250925110599', 'x': '7052.29224', 'tagName': 'pt'}, {'y': '338.250834235796', 'x': '7052.29224', 'tagName': 'pt'}, {'y': '338.251292301377', 'x': '7052.29224', 'tagName': 'pt'}], 'tagName': 'convexhull'}, {'value': '421', 'type': 'int', 'name': 'spectrum_index', 'tagName': 'userParam'}, {'value': 'controllerType=0 controllerNumber=1 scan=5342', 'type': 'string', 'name': 'spectrum_native_id', 'tagName': 'userParam'}]
        [{'content': '5109.29224', 'dim': '0', 'tagName': 'position'}, {'content': '336.251104824796', 'dim': '1', 'tagName': 'position'}, {'content': '234284', 'tagName': 'intensity'}, {'content': '0', 'dim': '0', 'tagName': 'quality'}, {'content': '0', 'dim': '1', 'tagName': 'quality'}, {'content': '225053', 'tagName': 'overallquality'}, {'content': '2', 'tagName': 'charge'}, {'nr': '0', 'nestedElement': [{'y': '336.125209180674', 'x': '5105.9217', 'tagName': 'pt'}, {'y': '336.124751115092', 'x': '5108.7642', 'tagName': 'pt'}, {'y': '336.124841989895', 'x': '5109.6031', 'tagName': 'pt'}, {'y': '336.12529301464', 'x': '5110.4848', 'tagName': 'pt'}, {'y': '336.124957942644', 'x': '5111.6874', 'tagName': 'pt'}, {'y': '338.251041063348', 'x': '5111.6874', 'tagName': 'pt'}, {'y': '338.251376135343', 'x': '5110.4848', 'tagName': 'pt'}, {'y': '338.250925110599', 'x': '5109.6031', 'tagName': 'pt'}, {'y': '338.250834235796', 'x': '5108.7642', 'tagName': 'pt'}, {'y': '338.251292301377', 'x': '5105.9217', 'tagName': 'pt'}], 'tagName': 'convexhull'}, {'value': '3916', 'type': 'int', 'name': 'spectrum_index', 'tagName': 'userParam'}, {'value': 'controllerType=0 controllerNumber=1 scan=18484', 'type': 'string', 'name': 'spectrum_native_id', 'tagName': 'userParam'}]
        [{'content': '4009.58726', 'dim': '0', 'tagName': 'position'}, {'content': '428.197275997238', 'dim': '1', 'tagName': 'position'}, {'content': '111429', 'tagName': 'intensity'}, {'content': '0', 'dim': '0', 'tagName': 'quality'}, {'content': '0', 'dim': '1', 'tagName': 'quality'}, {'content': '35753.2', 'tagName': 'overallquality'}, {'content': '2', 'tagName': 'charge'}, {'nr': '0', 'nestedElement': [{'y': '428.071338720547', 'x': '4001.7973', 'tagName': 'pt'}, {'y': '428.071177661641', 'x': '4004.4017', 'tagName': 'pt'}, {'y': '428.071136832932', 'x': '4009.2555', 'tagName': 'pt'}, {'y': '428.071491868401', 'x': '4014.7713', 'tagName': 'pt'}, {'y': '428.070943557216', 'x': '4017.7105', 'tagName': 'pt'}, {'y': '430.19702667792', 'x': '4017.7105', 'tagName': 'pt'}, {'y': '430.197574989105', 'x': '4014.7713', 'tagName': 'pt'}, {'y': '430.197219953635', 'x': '4009.2555', 'tagName': 'pt'}, {'y': '430.197260782345', 'x': '4004.4017', 'tagName': 'pt'}, {'y': '430.197421841251', 'x': '4001.7973', 'tagName': 'pt'}], 'tagName': 'convexhull'}, {'value': '2895', 'type': 'int', 'name': 'spectrum_index', 'tagName': 'userParam'}, {'value': 'controllerType=0 controllerNumber=1 scan=15394', 'type': 'string', 'name': 'spectrum_native_id', 'tagName': 'userParam'}]
        [{'content': '5107.29224', 'dim': '0', 'tagName': 'position'}, {'content': '337.251104824796', 'dim': '1', 'tagName': 'position'}, {'content': '556384', 'tagName': 'intensity'}, {'content': '0', 'dim': '0', 'tagName': 'quality'}, {'content': '0', 'dim': '1', 'tagName': 'quality'}, {'content': '225053', 'tagName': 'overallquality'}, {'content': '2', 'tagName': 'charge'}, {'nr': '0', 'nestedElement': [{'y': '337.125209180674', 'x': '5107.9217', 'tagName': 'pt'}, {'y': '337.124751115092', 'x': '5108.7642', 'tagName': 'pt'}, {'y': '337.124841989895', 'x': '5109.6031', 'tagName': 'pt'}, {'y': '337.12529301464', 'x': '5110.4848', 'tagName': 'pt'}, {'y': '337.124957942644', 'x': '5112.6874', 'tagName': 'pt'}, {'y': '339.251041063348', 'x': '5111.6874', 'tagName': 'pt'}, {'y': '339.251376135343', 'x': '5110.4848', 'tagName': 'pt'}, {'y': '339.250925110599', 'x': '5109.6031', 'tagName': 'pt'}, {'y': '339.250834235796', 'x': '5108.7642', 'tagName': 'pt'}, {'y': '339.251292301377', 'x': '5108.9217', 'tagName': 'pt'}], 'tagName': 'convexhull'}, {'value': '3916', 'type': 'int', 'name': 'spectrum_index', 'tagName': 'userParam'}, {'value': 'controllerType=0 controllerNumber=1 scan=18484', 'type': 'string', 'name': 'spectrum_native_id', 'tagName': 'userParam'}]

        """
        # Set the simpleFlag to false for __getitem__
        self.simpleFlag = False
        # reset elementKeySet (because this is hard coded in __init__ for getSimpleFeatureInfo)
        self.__elementKeySet = set()
        # counter for the amount of elements with a feature tag. If it stay 0 at the end of the yielding this function raises a runtime error
        featureCount = 0
        # for all the elements
        for element in self.getAllElements():
            # if the element is a feature
            if element.tag == 'feature':
                # keep a count of the amount of features
                featureCount += 1
                
                # get all the info from the feature element and put it in elementInfo
                self.elementInfo.update(elementFunctions.getAllNestedElementInformation(element))
                self.__elementKeySet = set(self.elementInfo.keys())
                # also yield the element so anyone can get any information out of it
                yield element
                # this gets called after every yield statement and clears every element that is under the current element. Because all the 
                # nested elements of the current element have already been used and the results saved in self.elementInfo, they are not
                # necessary anymore and clearing them lowers the memory usage. 
                for nestedElement in element:
                    nestedElement.clear()
                element.clear()

        if elementCount == 0:
            raise RuntimeError, 'There were no features found in self.getAllElements(). Not a valid featureXML file:'+str(self.path)

      
    # get all elements that are not features
    def getNonConsensusElements(self):
        """
        Iterator function that yields all the non-feature elements in the file given to Reader()

        @rtype: Element
        @return: Iterator of all the elements in the file where element.tag != 'feature'

        B{Example}:
        
        Printing all the non-features in a file:

        >>> featureXML = Reader('example_feature_file.featureXML')    # make a reader instance
        >>> features = featureXML.getNonFeatureElements()                     # get all non-features
        >>> for element in features:
        ...    print element
        <Element 'software' at 0x166a05a0>
        <Element 'processingAction' at 0x166a0600>
        """
        # for all the elements
        for element in self.getAllElements():
            # if the element is not a feature
            if not element.tag.startswith('consensusElement'):
                yield element


    # Return the keys that can be used by __getitem__
    def getKeys(self):
        """
        Return the set of keys that can be used as a key on a Reader instance
        
        @rtype: Set
        @return: All usable Reader instance keys
        
        B{Example}:
        
        Printing the keys that can be used to get information from a feature:
        
        >>> featureXML = Reader('example_feature_file.featureXML')    # make a reader instance
        >>> featureXML.getKeys()
        set(['convexhull', 'charge', 'content', 'intensity', 'position', 'overallquality', 'userParam', 'quality', 'id'])
        """
        return self.__elementKeySet
    
    
    # Return all the feature id's
    def getAllFeatureId(self):
        """
        Iterator function that yields all feature Ids

        @rtype: string
        @return: Iterator of all the id's in the file
        @raise RuntimeError: No feature id's in the file

        B{Example}:

        Print all the feature ids in a file:

        >>> featureXML = Reader('example_feature_file.featureXML')    # make a reader instance
        >>> for id in featureXML.getAllFeatureId():
        ...    print id
        f_13020522388175237334
        f_8613715360396561740
        f_43922326584371237334
        """
        # a counter to keep track of the amount of feature id's. If it it 0 at the end, raise a runtime error
        countFeatureId = 0
        # for all the features in the called instance
        for features in self.getSimpleFeatureInfo():
            countFeatureId += 1
            # yield the id of that feature element
            yield self.elementInfo[self.element]['id']
        if countFeatureId == 0:
            raise RuntimeError, 'There were no feature id found in self.getAllFeatureId(). Not a valid featureXML file'


    def getElementInfo(self):
        """
        Return self.elementInfo.
        
        @rtype: dict
        @return: self.elementInfo
        """
        return self.elementInfo[self.element]

    # Make it possible to get a value with instance[value], because self.element is already given
    def __getitem__(self,key):
        """
        'Magic' function to make it possible to get information from an element using dictionary [key] syntax
                
        @type key: string
        @param key: Name of the value to get information from
        @return: The [key] value of the current element
        @raise RuntimeError: The value given to __getitem__ is not a string
        @raise KeyError: key given to __getitem__ does not exist in self.elementInfo 
        
        B{Example}:
        
        Print the feature id and intensity, making use of the dictionary [key] sytax:
        
        >>> consensusXML = Reader('example_consensus_file.consensusXML')   # make a Reader instance
        >>> features = featureXML.getFeatures()                    # get all the features of the Reader instance
        >>> for feature in features:                               # loop through all the features
        ...     print 'intensity of', featureXML['id'],' = ', featureXML['intensity']    # print the id and intensity of the feature
        intensity of f_13020522388175237334  =  524284
        intensity of f_8613715360396561740  =  111329
        intensity of f_43922326584371237334  =  524284
        """
        # if simpleFlag is True, features were retrieved by simpleFeatureInfo
        if self.simpleFlag:
            if type(key) != str:
                raise RuntimeError, 'The value in __getitem__ has to be a string. It is: '+str(type(key))
            key = key.lower()
            if key.lower() == 'userparam':
                key = 'userParam'
            try:
                return self.elementInfo[self.element][key]
            except KeyError:
                raise KeyError, 'key "%s" given to parseConsensusXML[<key>] does not exist in elementInfo. The possible keys are: '%key +str(self.getKeys())
        
        # elif simpleFlag is False, feature were retrieved by allFeatureInfo
        elif not self.simpleFlag:
            try:
                return self.elementInfo[key]
            except KeyError:
                raise KeyError, 'key "%s" given to parseFeatureXML[<key>] does not exist in elementInfo. The possible keys are: '%key +str(self.getKeys())
        else:
            raise RuntimeError, 'This should not happen, self.simpleFlag in parseFeatureXML is a bool and should either be True or False, not: '+str(simpleFlag)
      
            

             
