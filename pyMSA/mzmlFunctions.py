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
Functions to extract information from pymzml.run.Reader() instances
"""
# author: deklein
# date:10/02/2012
# summary: testing mzml parsing using py

import sys
# to be able to import pymzml from a locally installed pymzml
try:
    sys.path.append('/homes/ndeklein/python2.6/site-packages')
except:
	pass
import pymzml
import collections
import getWindow
import elementFunctions
import base64

# get the retention time and m/z value of all ms/ms precursors from an msrun
def getPrecursorRtMz(msrun):
    """
    
    Get the retention time of all MS/MS precursors in an instance of a pymzml.run.Reader().
    
    @type msrun: pymzml.run.Reader() instance
    @param msrun: Iterator object containing information on a .mzML file 
    @rtype: List of dictionaries
    @return: The paired retention time and m/z values.
    @raise TypeError: msrun not an instance of pymzml.run.Reader()
    @raise RuntimeError: msrun contained 0 spectra with ms level 2
    
    B{Examples}:
    
    Print the dictionary containing all the retention time and m/z pairs in a file:
    
    >>> import pymzml
    >>> msrun = pymzml.run.Reader('example_mzML_file.mzML')    # pymzml.run.Reader instance
    >>> print getPrecursorRtMz(msrun)
    [{'rt': 85.166666666666671, 'mz': '337.33999999999997'}, {'rt': 0.82813999999999999, 'mz': '421.76077270507812'}]
    
    Print all the retention times in a file (only uses the pymzml package):
    
    >>> import pymzml
    >>> msrun = pymzml.run.Reader('example_mzML_file.mzML')    # pymzml.run.Reader instance
    >>> for values in msrun:
    ...    print values['scan time']
    85.166666666666671
    0.82813999999999999
    421.76077270507812
    """
    if isinstance(msrun, pymzml.run.Reader): # check that msrun is the right instance
        # list to keep al the retention times
        retentionTimeList = []
        # a counter to keep track of the amount of precursors with ms level of 2
        countMS = 0 
        # for all the spectrums in msrun
        for spectrum in msrun:
            # if the spectrum is of level 2 (ms/ms)
            if spectrum['ms level'] == 2:
                # keep track of the amount of MS precursors
                countMS += 1
                # for all the precursors in the spectrum
                for precursor in spectrum['precursors']:
                    # append the spectrum retention time (MSL1000016, in minutes) and the m/z ratio to the list
                    retentionTimeList.append({'rt':spectrum['MS:1000016'], 'mz':precursor['mz']})
        
        # if there were no spectra with an ms level of 2 raise an  
        if countMS == 0:
            raise RuntimeError, 'The msrun given to getPrecursorRtMz contained 0 spectra with ms level 2. '
        else:
            return retentionTimeList
    else:
        # raise a typeError
        raise TypeError, 'msrun given to getPrecursorRtMz is not an instance of pymzml.run.Reader. It is of type: '+str(type(msrun))


# get the a list of keys from an instance of a pymzml.run.Reader(mzml file) excluding the keys given
def getKeys(msrun, excludeList = [], includeList = []):
    """
    
    Get a list of keys from an instance of a pymzml.run.Reader() that is not in the excludeList and which don't start with MS.
    Return three lists, one with the keys of the spectrum, one with the keys of the precursors and one with the spectrums that have been looped through. 
    This way the information from these spectrums aren't missed (because pymzml's sprectrum class works like a generator, information that has been looped through is lost).
    
    @type msrun: pymzml.run.Reader() instance
    @param msrun: Iterator object containing information on a .mzML file 
    @type excludeList: list
    @param excludeList: Keys to exclude (default = [])
    @type includeList: list
    @param includeList: Keys to include (default = [])
    @rtype: Two tuples and a list
    @return: One tuple with the keys of the spectrum, one tuple with the keys of the precursors and one list with the spectrums that have been looped through. 
    @raise TypeError: excludeList or includeList is not of type list

    B{Examples}:
    
    Get the spectrumKeys, precursorKeys and spectrumList from a pymzml.run.Reader instance and print the spectrumKeys and precursorKeys
    
    >>> import pymzml
    >>> msrun = pymzml.run.Reader('example_mzML_file.mzML')    # pymzml.run.Reader instance
    >>> spectrumKeys, precursorKeys, spectrumList = getKeys(msrun)
    >>> print spectrumKeys
    ['no compression', 'total ion current', 'scan time', 'filter string', 'precursors', 'id', 'profile mass spectrum', 'collision-induced dissociation', '64-bit float', 'defaultArrayLength', 'm/z array', 'charge state', 'None', 'ms level', 'intensity array', 'BinaryArrayOrder', 'charge', 'mz']
    >>> print precursorKeys
    ['charge', 'mz']

    Get the spectrumKeys, precursorKeys and spectrumList from a pymzml.run.Reader instance, excluding certain keys, and print the spectrumKeys and precursorKeys

    >>> import pymzml
    >>> msrun = pymzml.run.Reader('example_mzML_file.mzML')    # pymzml.run.Reader instance
    >>> spectrumKeys, precursorKeys, spectrumList = getKeys(msrun, excludeList = (['scan time', 'filter string', 'PY:0000000', 'precursors', 'id', 'profile mass spectrum', 'charge','collision-induced dissociation', '64-bit float', 'defaultArrayLength', 'm/z array', 'charge state', 'None', 
                                                            'ms level', 'intensity array', 'BinaryArrayOrder', 'encodedData', 'mz'])
    >>> print spectrumKeys 
    ['no compression', 'total ion current']
    >>> print precursorKeys
    []
 
    Get the spectrumKeys, precursorKeys and spectrumList from a pymzml.run.Reader instance, excluding I{and} including certain keys, and print the spectrumKeys and precursorKeys    
    
    >>> import pymzml
    >>> msrun = pymzml.run.Reader('example_mzML_file.mzML')    # pymzml.run.Reader instance
    >>> spectrumKeys, precursorKeys, spectrumList = getKeys(msrun, excludeList = (['scan time', 'filter string', 'PY:0000000', 'precursors', 'id', 'profile mass spectrum', 'collision-induced dissociation', '64-bit float', 'defaultArrayLength', 'm/z array', 'charge state', 'None', 'ms level', 
                                                            'intensity array', 'BinaryArrayOrder', 'encodedData', 'mz'], includeList = ['includeKey','includeAnotherKey'])
    >>> print spectrumKeys 
    ['no compression', 'total ion current', 'charge', 'includeKey', 'includeAnotherKey']
    >>> print precursorKeys
    ['charge']
    
    
    """
    # check that excludelist and includelist are of the type list, because of pythons duck typing this can be overwritten. If they are not lists, raise a typeerror
    if not type(excludeList) == list or not type(includeList) == list:
        raise TypeError, 'excludeList and includeList given to getKeys have to be lists. They were: excludeList: '+str(type(excludeList))+' and includeList: '+str(type(includeList))
    
    # spectrumList will contain a list of the spectrum through which it looped
    spectrumList = []
    
    # spectrumKeys will contain the column header names
    spectrumKeys = set([])
    precursorKeys = set([])
    # flag to get out of nested loop
    done = False
    for spectrum in msrun:
        spectrumList.append(spectrum.deRef()) 
        # if flag done == True break the loop
        if done:
            break
        # for all the keys in spectrum
        for key in spectrum:
            # if the key is not in the list of headers not to be included and key does not start with MS:
            if key not in excludeList and not key.startswith('MS:'): 
                # append the key to spectrum keys
                spectrumKeys.add(key)

        # if the spectrum has a MS/MS precursor
        if spectrum['ms level'] == 2:
            # make a precursor keys variable
            for key in spectrum['precursors'][0].keys():
                if key not in excludeList: # if the precursor key is not in the exclude list
                    precursorKeys.add(key)
                    spectrumKeys.add(key)
            # set done flag to true
            done = False
            break
    # adding the keys from includeList
    for key in includeList:
        spectrumKeys.add(key)
        
    return spectrumKeys, precursorKeys, spectrumList


# count the # of occurences of each charge state
def getChargeStateAbundance(msrun):
    """    
    Get the abundance of each charge state in msrun
    
    @type msrun: pymzml.run.Reader() instance
    @param msrun: Iterator object containing information on a .mzML file 
    @rtype: dict
    @return: The abundance of all the charge states in msrun 
    
    B{Example}:
    
    Get the charge states of msrun
        
    >>> import pymzml
    >>> msrun = pymzml.run.Reader('example_mzML_file.mzML')    # pymzml.run.Reader instance
    >>> abundance = getChargeStateAbundance(msrun)
    >>> print abundance
    {'3': 3920, '2': 10099, '5': 148, '4': 647, '7': 3, '6': 41}
    
    """
    # defaultdict to keep track of the abundance of each charge state
    abundanceDict = collections.defaultdict(int)
    # loop through all the spectra in msrun
    for spectrum in msrun:
        # because only MS/MS have charge state, only use that
        if spectrum['ms level'] == 2:
            # get the charge state of this spectrum and count one up in the abundanceDict for that charge state
            abundanceDict[spectrum['precursors'][0]['charge']] += 1
    
    return dict(abundanceDict)
    
# get the total amount of MS and MS/MS
def getTotalMScount(msrun):
    """
    Get the total amount of MS and MS/MS measurements in msrun
    
    @type msrun: pymzml.run.Reader() instance
    @param msrun: Iterator object containing information on a .mzML file 
    @rtype: dict
    @return: Total amount of MS and MS/MS
    
    B{Example}:
    
    Get the total amount of MS and MS/MS in msrun
        
    >>> import pymzml
    >>> msrun = pymzml.run.Reader('example_mzML_file.mzML')    # pymzml.run.Reader instance
    >>> msCount = getTotalMScount(msrun)
    >>> print msCount
    {"MS":231, "MS/MS", 2315}
    """
    msDict = {'MS':0, 'MS/MS':0}
    for spectrum in msrun:
        if not spectrum['id'] == 'tic' and not spectrum['id'] == 'sic':
            if spectrum['ms level'] == 1:
                msDict['MS'] += 1
            elif spectrum['ms level'] >= 2:
                msDict['MS/MS'] += 1
            else:
                raise RuntimeError, 'This should not happen, ms level in msrun given to getTotalMScount should always be 1 or higher. It was: '+str(spectrum['ms level'])
    return msDict


class IntensityFromSpectra:
    """
    Put getIntensityFromMZwindow in a class to be able to initialize mzmlInstance once. Because it empties when it's looped through, 
    if the same mzmlInstance is used multiple times the function only works once. By putting it in the __init__ and making the class only once
    the same mzmlInstance can be used multiple times (although copies of the spectra have to be made).
    """
    
    def __init__(self, mzmlInstance):
        """
        @type mzmlInstance: pymzml.run.Reader
        @param mzmlInstance: Instance of pymzml.run.Reader class which you want to use to plot the XIC from
        @raise TypeError: mzmlInstance not of type pymzml.run.Reader
        """
        if not isinstance(mzmlInstance, pymzml.run.Reader):
            raise TypeError, 'mzmlInstance given to massWindow_XIC_plot is not of type pymzml.run.Reader(). Instead, is of type: '+str(type(mzmlInstance))

        self.mzmlInstance = mzmlInstance
        self.spectrumLocation = None
        
    def getIntensityFromMZwindow(self, lowerMass, upperMass):
        """
        Get the summed intensity per run time. Iterate through the spectra, take the MS1 spectrum, isolate the mass range and sum the intensity, 
        returning the sum of intensity and RT as a dictionary (with RT as key, intensity as value).
     
        Essentially you are taking the area under the intensity-m/z curve as the single intensity point.
    
        @type lowerMass: Number
        @param lowerMass: The lower boundary of the m/z window to calculate the XIC over
        @type lowerMass: Number
        @param lowerMass: The upper boundary of the m/z window to calculate the XIC over
        @raise TypeError: lowerMass not of int
        @raise TypeError: upperMass not of type int
        @raise RuntimeError: No spectra with MS 1 in that window
        @rtype: Two lists
        @return: List of retention times and corresponding summed intensity. Both are sorted.
        
        B{Example:}
        
        >>> import pymzml
        >>> mzmlInstance = pymzml.run.Reader('/example_file.mzML')
        >>> print massWindow_XIC_plot(mzmlInstance, 800, 804)
        """
        if not isinstance(lowerMass, int) and not isinstance(lowerMass, float):
            raise TypeError, 'lowerMass given to massWindow_XIC_plot is not of type int or float. Instead, is of type: '+str(type(lowerMass))
        if not isinstance(upperMass, int) and not isinstance(upperMass, float):
            raise TypeError, 'upperMass given to massWindow_XIC_plot is not of type int or float. Instead, is of type: '+str(type(upperMass))
            
        if not self.spectrumLocation:
            self.spectrumLocation = getWindow.SpectraLocation(self.mzmlInstance)
    
        # dict of intensity per retention time (retention time as key,  intensity as value). Is defaultdict so intensity can be added to the value to sum
        intensityDict = collections.defaultdict(int)
        
        # counter for # of spectra
        specCount = 0
        for spectrum, intensity in self.spectrumLocation.getSpectra_mzWindow(lowerMass, upperMass):
            if spectrum['ms level'] > 1:
                # make seconds out of the retention time and use as key in dict. sum the intensity
                intensityDict[(float(spectrum['scan time'])*60)] += float(intensity)
                specCount += 1
        
        if specCount == 0:
            raise RuntimeError, 'No spectra with MS level 1 in that mz window'
        
        # sort the keys of intensityDict
        sortedRetentionTime = sorted(intensityDict.iterkeys())
        sortedIntensity = []
        for key in sortedRetentionTime:
            sortedIntensity.append(intensityDict[key])
        
        del intensityDict
        
        return sortedRetentionTime, sortedIntensity

