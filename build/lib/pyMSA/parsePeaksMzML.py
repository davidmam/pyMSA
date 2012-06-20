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
Parser to extract relevant data from a .peaks.mzML file.
"""

# author: ndeklein
# date:08/02/2012
# summary: Parses a .peaks.mzML file. Makes an iterator object out of the parsing (using yield, not __iter__ and __next__).
from xml.etree import cElementTree
import fileHandling
import collections
import elementFunctions

class Reader():
    """
    
    Generator object with functions to acces information from peaks.mzML files easily. For a big part it could be done using pymzml, the problem 
    being that .peaks.mzML file have the following format for some of the relevant values (but not for all...)::
        <cvParam cvRef="MS" accession="MS:1000504" name="base peak m/z" value="350.98370361328125" unitCvRef="MS" unitAccession="MS:1000040" unitName="m/z"/>
        <cvParam cvRef="MS" accession="MS:1000505" name="base peak intensity" value="24486.63671875" unitCvRef="MS" unitAccession="MS:1000131" unitName="number of counts"/>
        <cvParam cvRef="MS" accession="MS:1000285" name="total ion current" value="130991.71875"/>
        <cvParam cvRef="MS" accession="MS:1000528" name="lowest observed m/z" value="335.00112820357106" unitCvRef="MS" unitAccession="MS:1000040" unitName="m/z"/>
        <cvParam cvRef="MS" accession="MS:1000527" name="highest observed m/z" value="1807.2383440459291" unitCvRef="MS" unitAccession="MS:1000040" unitName="m/z"/>
    
    instead of mzML's format of the same values::
        <userParam name="base peak m/z" type="xsd:double" value="350.983703613281"/>
        <userParam name="base peak intensity" type="xsd:double" value="24486.63671875"/>
        <userParam name="total ion current" type="xsd:double" value="130991.71875"/>
        <userParam name="lowest observed m/z" type="xsd:double" value="335.001128203571"/>
        <userParam name="highest observed m/z" type="xsd:double" value="1807.23834404593"/>
                            
     
    pymzML does not find these differently formatted values. It would probably be easy to change this in pymzml, but for clarity I want to keep this separated.
    
    
    Reader() applies a __getitem__ function so information can be retrieved from the feature elements
    using the dictionary [key] syntax. 
    
    B{Example}
    
    Print feature id and intensity example with example output:
    
    >>> peaksMzML = Reader('example_peaks_file.peaks.mzML')   # make a Reader instance
    >>> spectra = peaksMzML.getSpectra()                    # get all the spectra of the Reader instance
    >>> for spectrum in spectra:                            # loop through all the spectra
    ...     print 'total ion current of', peaksMzML['id'],' = ',peaksMzML['total ion current']    # print the id and ion current of the spectrum

    B{<TODO>}
    
    Do something about the minute-second interchangability between peaks, features and spectra
 
    B{To change (?)} 
    
    The class is a bit weirdly designed, because it has both the generator functions and the __getitem__ function you need to loop through the
    spectra but then use the Reader instance to get the item (see the example, for spectrum in spectra: peaksMzML['id']). This can be changed
    by having a different class called spectrum (maybe use pymzml's spec, but then again, I didn't use pymzml's spec because it wasn't working) 
    which has a __getitem__ function, and yield the spectrum from the Reader instance. However, this method I{does} work, so it is not high on 
    priority (unless it causes a lot of confusion with the user). Same goes for L{parseFeatureXML.Reader}.
        
    """
    
    
    # initializer, takes a file path as input
    def __init__(self, path):
        """
        Initialize the Reader instance and check if the file is a valid peaks.mzML file and put it in a fileHandling.FileHandle instance.
        
        @type path: string
        @param path: The path of the feature XML file                       

        """
        
        # filepath
        self.path = path
        # if the file at path does not start with <?xml, raise an exception that the xml file is invalid
        file = fileHandling.FileHandle(self.path)
        file.isXML()
        file.isMzML()
        # the current element
        self.element = None
        # current userParam
        # a list of all the keys that can be used for __getItem__
        self.__spectraKeySet = []
        # element dictionary to contain all the elements
        # uses collections.defaultidct to enable unknown keys to be added to the dictionary 
        self.spectraInfo = collections.defaultdict(dict)
        
        self.simpleFlag = True

    # Make an iterable function (by using yield) that returns every element in the file
    def getAllElements(self):
        """
        Iterator function that yields all the elements in the file given to Reader()
        
        @rtype: Element
        @return: Iterator of all the elements in the file
        @raise RuntimeError: No elements in the file

        B{Example}:

        Printing all elements in a file:
        
        >>> featureXML = Reader('example_feature_file.featureXML')    # make a read instance
        >>> allElements = featureXML.getAllElements()    # get all elements of the reader instance, you can now iterate over allElements
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
            self.spectraInfo.clear()
            yield element
        element.clear()
        # when doing -> for i in readerInstance.getElement, the last loop goes to file.close()
        inFile.close()
        
        # this should never be able to happen because of file.isXML and file.isFeatureXML in the __init__
        if elementCount == 0:
            raise RuntimeError, 'No elements found at getAllElements(), invalid featureXML file: '+str(self.path)




    # Get the items from getElements, only yield the feature elements
    # Add extra feature specific info to self.elementInfo
    def getSimpleSpectraInfo(self):
        """
        Iterator function that yields all the feature elements in the file given to Reader()
        It saves info from the features in a dict, self.spectraInfo, which is used in the L{Reader.__getitem__} retrieval function.
        This function has predefined information like intensity, overallquality, convexhull etc that make for easier browsing, but because of this
        it does not contain all information. If you want to get all information exactly as found in the xml file, use L{parsePeaksMzML.Reader.getAllSpectraInfo}.  
        
        @rtype: Element
        @return: Iterator of all the elements in the file where element.tag == 'spectrum'
        @raise RuntimeError: No features in the file
        
        B{Example}:
        
        Print all the information of all the MS/MS spectra in examplePeaksfile.peaks.mzML. Only showing one result:
        
        >>> peaksMzML = Reader('example_peaks_file.peaks.mzML')   # make a Reader instance
        >>> spectra = peaksMzML.getSpectra()                    # get all the spectra of the Reader instance
        ...     for spectrum in spectra:                               # loop through all the spectra
        ...        if int(peaksMzML['ms level']) == 2:
        ...            for keys in peaksMzML.getKeys():
        ...                print 'key: '+str(keys)+'\tvalue: '+str(peaksMzML[keys])
        ...            print '-'*20
        key: scan_id    value: 1
        key: centroid spectrum    value: centroid spectrum
        key: ms level    value: 2
        key: mass spectrum    value: mass spectrum
        key: positive scan    value: positive scan
        key: base peak m/z    value: 368.750823974609
        key: base peak intensity    value: 37719.2890625
        key: total ion current    value: 110887.0078125
        key: lowest observed m/z    value: 108.770645141602
        key: highest observed m/z    value: 754.29296875
        key: filter string    value: ITMS + c NSI d Full ms2 377.67@cid35.00 [90.00-770.00]
        key: preset scan configuration    value: 4
        key: no combination    value: no combination
        key: scan start time    value: 1158.9672
        key: [thermo trailer extra]monoisotopic m/z:    value: 377.673858642578
        key: scan window lower limit    value: 90
        key: scan window upper limit    value: 770
        key: isolation window target m/z    value: 377.673858642578
        key: isolation window lower offset    value: 1
        key: isolation window upper offset    value: 1
        key: selected ion m/z    value: 377.673858642578
        key: charge state    value: 2
        key: peak intensity    value: 55344.1875
        key: activation energy    value: 0
        key: collision-induced dissociation    value: collision-induced dissociation
        key: collision energy    value: 35
        """
        # counter for the amount of elements with a userparam tag. If it stay 0 at the end of the yielding this function raises a runtime error
        userParamCount = 0
        # looping through all the elements to get the cvParam and userParam of the element
        for element in self.getAllElements():
            # get the spectrum elements
            if element.tag.split('}')[1] == 'spectrum':
                # reset the keyset
                self.__spectraKeySet = []
                # First I only took things that I thought would be useful for analyzing, but maybe someone at some point needs to know if it was a positive or a negative scan
                # and it is better practice to have everything in already and deal with what is needed later. So this uses an recursive function to get all items of all elements
                # that are nested in the first element    
                for info in elementFunctions.getAllNestedItems(element):
                    if info.has_key('name'):
                        # some dicts have a name but not a value, that case the name is also the value (more informative than just null
                        if not info.has_key('value'):       
                            value = info['name']
                        else:
                            value = info['value']
                        self.spectraInfo[element][info['name'].lower()] = value
                        self.__spectraKeySet.append(info['name'].lower())   
                    # setting the id to a number instead of a big string (there is mroe in front of scan=                 
                    elif info.has_key('id'):
                        self.spectraInfo[element]['scan_id'] = info['id'].split('scan=')[1]
                        self.__spectraKeySet.append('scan_id')
                yield element
                # this gets called after every yield statement and clears every element that is under the current element. Because all the 
                # nested elements of the current element have already been used and the results saved in self.elementInfo, they are not
                # necessary anymore and clearing them lowers the memory usage. 
                for nestedElement in element:
                    nestedElement.clear()
                element.clear()
 
    # Get the items from getElements, only yield the feature elements
    # Add extra feature specific info to self.elementInfo
    def getAllSpectraInfo(self):
        """
        Iterator function that yields all the feature elements in the file given to Reader().
        It saves info from the features in a dict, self.spectraInfo, which is used in the L{Reader.__getitem__} retrieval function.
        This function gets all the information from a feature element and does no processing. Because of this the key names are not very intuitive.
        If you want a more intuitive key-name system, use L{parsePeaksMzML.Reader.getSimpleSpectraInfo}. That comes at the cost of loss of information though. 
    
        @rtype: Element
        @return: Iterator of all the elements in the file where element.tag == 'spectrum'
        @raise RuntimeError: No features in the file
        
        B{Example}:

        <TODO>

        """
        # Set the simpleFlag to false for __getitem__
        self.simpleFlag = False
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
                
                # also yield the element so anyone can get any information out of it
                yield element
                # this gets called after every yield statement and clears every element that is under the current element. Because all the 
                # nested elements of the current element have already been used and the results saved in self.elementInfo, they are not
                # necessary anymore and clearing them lowers the memory usage. 
                for nestedElement in element:
                    nestedElement.clear()
                element.clear()

        if featureCount == 0:
            raise RuntimeError, 'There were no features found in self.getAllElements(). Not a valid featureXML file:'+str(self.path)

                

      
    # Return the keys that can be used by __getitem__
    def getKeys(self):
        """
        Return the set of element keys that can be used as a key on a Reader instance
        
        @rtype: Set
        @return: All usable Reader instance keys
        
        B{Example}:
        
        Printing the keys that can be used to get information from all spectra. Removed part of the result for ... for clarity:
        
        >>> peaksMzML = Reader('example_peaks_file.peaks.mzML')   # make a Reader instance
        >>> spectra = peaksMzML.getSpectra()                    # get all the spectra of the Reader instance
        >>> for spectrum in spectra:
        ...    print peaksMzML.getKeys()
        [...,'preset scan configuration', 'no combination', 'scan start time', '[thermo trailer extra]monoisotopic m/z:', 'scan window lower limit', 'scan window upper limit', 'isolation window target m/z', 'isolation window lower offset', ...]
        [...,'preset scan configuration', 'no combination', 'scan start time', '[thermo trailer extra]monoisotopic m/z:', 'scan window lower limit', 'scan window upper limit', 'isolation window target m/z', 'isolation window lower offset', ...]
        [...,'preset scan configuration', 'no combination', 'scan start time', 'scan window lower limit', 'scan window upper limit', 'm/z array', '64-bit float', 'no compression', 'intensity array', '32-bit float', 'no compression']
        """
        if len(self.__spectraKeySet) == 0:
            raise (RuntimeError, 'You have to use .getSpectra() and loop through the spectra before using.getKeys(). It is unknown which keys will be available now,'+
                                 +'because this is different for different spectra. See documentation for further details.')
        return self.__spectraKeySet
    


    # Make it possible to get a value with instance[value], because self.element is already given
    def __getitem__(self,key):
        """
        'Magic' function to make it possible to get information from an element using dictionary [key] syntax
                
        @type key: string
        @param key: Name of the value to get information from
        @return: The [key] value of the current element
        @raise Exception: The value given to __getitem__ is not a string
        
        B{Example}:
        
        Print the spectrum id and base peak intensity, making use of the dictionary [key] sytax:
        
        >>> peaksMzML = Reader('example_peaks_file.peaks.mzML')   # make a Reader instance
        >>> spectra = peaksMzML.getSpectra()                    # get all the spectra of the Reader instance
        >>> for spectrum in spectra:                            # loop through all the spectra
        ...     print 'base peak intensity intensity of', peaksMzML['scan_id'],' = ', ['base peak intensity']    # print the id and intensity of the feature
        base peak intensity intensity of 1133  =  4176.33203125
        base peak intensity intensity of 1134  =  203653.625
        base peak intensity intensity of 1135  =  14828.59765625
        """
        if self.simpleFlag:
            if type(key) != str:
                raise Exception, 'The value in __getitem__ has to be a string. It is: '+str(type(key))
            key = key.lower()
            try:
                return self.spectraInfo[self.element][key]
            except KeyError:
                raise KeyError, '\''+str(key)+'\' is not found in peaksMzML. The usable keys are: '+str(self.spectraInfo[self.element].keys())
        
        elif not self.simpleFlag:
            return self.spectraInfo[key]
    
    
