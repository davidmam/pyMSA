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
Functions that get information out of cElementTree elements
"""

# author: ndeklein
# date:08/02/2012
# summary: functions to get information from elements
import collections

def getItems(element):
    """
    Make a dictionary out of the items of I{one} element, with index 0 of the itemslist as key and index 1 of the itemslist as value. This is an 
    element as returned by the pymzml parsing of an mzml file
    
    @type element: Element from cElementTree
    @param element: Element
    @rtype: dictionary
    @return: The items of element
    @raise TypeError: element if not of type 'Element'
    
    B{Example}:

    Print the items of all the elements in a featureXML file

    >>> from xml.etree import cElementTree
    >>> elementFile = open('example_feature_file.featureXML')
    >>> for event, element in cElementTree.iterparse(elementFile):
    ...    print getItems(element)
    {'version': '1.8.0', 'name': 'FeatureFinder'}
    {'name': 'Quantitation'}
    >>> elementFile.close()
    
    """    
    if str(type(element)) != '<type \'Element\'>':
        raise TypeError, 'element in getItems(element) has to be type Element. It is: '+str(type(element))
        
    itemDict = {}
    for item in element.items():
        # make a dict out of the tuple because that is easier to work with
        itemDict[item[0]] = item[1]
    return itemDict        
    
    
def getAllNestedItems(element, structuredDict = {}):
    """
    Use L{getItems} to make a dictionary out of the items of the element, Then, loop through the element and recursively call getAllNestedItems. 
    This way, all the items of all the elements nested in element get returned.
    getAllNestedItems is a generator objects that yields a dictionary, so you have to loop through the results.
    
    @type element: Element from cElementTree
    @param element: Element
    @rtype: dict
    @return: All the key-value pairs found in element (using L{getItems})
    @raise TypeError: element if not of type 'Element'
        
    B{Example}:

    Print the items of all the elements nested in element of an example xml file:

    >>> import cElementTree
    >>> for event, element in cElementTree.iterparse('example_file.xml')
    ...    for info in getAllNestedItems(element):
    ...        print info
    {'index': '0', 'defaultArrayLength': '250', 'id': 'controllerType=0 controllerNumber=1 scan=1', 'dataProcessingRef': 'dp_sp_0'}
    {'cvRef': 'MS', 'accession': 'MS:1000127', 'name': 'centroid spectrum'}
    {'cvRef': 'MS', 'accession': 'MS:1000511', 'value': '1', 'name': 'ms level'}
    {'cvRef': 'MS', 'accession': 'MS:1000294', 'name': 'mass spectrum'}
    {'cvRef': 'MS', 'accession': 'MS:1000130', 'name': 'positive scan'}
    """
    # get the items of element and yield them back. Because code after yield is still processed, this means
    # that the items get returned out of the recursive function without breaking the recursion
    yield getItems(element)
    elementName = element.tag.split('}')[1]

    # get all elements that are in element
    for nestedElement in element:
        structuredDict[elementName] = elementName
        # loop through all the elements in getAllNestedItems (because i is yielding you can get items from the same function)
        for dict in getAllNestedItems(nestedElement):
            yield dict
         

def getAllNestedElementInformation(element):
    """
    Gets all the value and content information of the element and all the elements that are in the element, and maintains
    the nested structure. So if an xml file looks like this::
    <element1 name="centroid spectrum">
        <element2 count=1>
            <element3>Content</element3>
        </element2>
    </element1>
    The resulting dict will look like: {element:{'name':'centroid spectrum', 'nestedElement':{element2:{count=1}, 'nestedElement':{element3:{content='Content'}}}}}
    The values of the inner items are found using L{getItems} and the content is found using .text. All element dicts have a value tagName found by element.tag.
  
    @type element: Element from cElementTree
    @param element: Element
    @rtype: dict    
    @return: A dict which contains the structure and information of the elements and its nested elements.
    
    B{Example}:

    Getting the dictionary of one element with the information of itself and all sub-elements:
    
    >>> import cElementTree
    >>> for event, element in cElementTree.iterparse('example_file.xml')
    ...    for info in getAllNestedElementInformation(element):
    ...        print getAllNestedElementInformation(element)
    defaultdict(<type 'dict'>, {<Element '{http://psi.hupo.org/ms/mzml}spectrum' at 0x16015d50>: {'index': '1', 'nestedElement': defaultdict(<type 'dict'>, {<Element '{http://psi.hupo.org/ms/mzml}binaryDataArrayList' at 0x1601c930>: {'count': '2', 'nestedElement': defaultdict(<type 'dict'>, {<Element '{http://psi.hupo.org/ms/mzml}binaryDataArray' at 0x1601cc90>: {'nestedElement': defaultdict(<type 'dict'>, {<Element '{http://psi.hupo.org/ms/mzml}cvParam' at 0x1601ce70>: {'cvRef': 'MS', 'accession': 'MS:1000576', 'tagName': '{http://psi.hupo.org/ms/mzml}cvParam', 'name': 'no compression'}}), 'tagName': '{http://psi.hupo.org/ms/mzml}binaryDataArray', 'encodedLength': '3004'}}), 'tagName': '{http://psi.hupo.org/ms/mzml}binaryDataArrayList'}}), 'defaultArrayLength': '563', 'id': 'controllerType=0 controllerNumber=1 scan=2', 'tagName': '{http://psi.hupo.org/ms/mzml}spectrum'}})
    """
    
    # nestedDict contains the information of the 'parent' element and all the child elements
    infoDict = {'tagName':element.tag}
    infoDict.update(getItems(element))
    if element.text != None:
        if element.text.strip() != '':
            infoDict.update({'content':element.text})
    
    infoDict['nestedElement'] = []
    
    # loop through all the nestedElement in element. Because getAllNesteElementInformation gets called in this loop, it will go down to the last nestedElement
    # of the fest nestedElement before it goes to the next nestedElement of element
    for nestedElement in element:
        # recursion
        infoDict['nestedElement'].append(getAllNestedElementInformation(nestedElement))
    
    # if infoDicts nestedElements is empty, remove the key
    if not infoDict['nestedElement']:
        del(infoDict['nestedElement'])
    return infoDict
