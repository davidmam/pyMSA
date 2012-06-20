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
Classes to get a certain 'window' of information out of featureXML, mzML or peaks.mzML file.
"""

# author: ndeklein
# date:27/03/2012
# summary: Classes to get a certain 'window' of information out of featureXML, mzML or peaks.mzML file.
import elementFunctions
import copy
import bisect
import time

class FeatureLocation:
    """
    Several functions to retrieve a list of features in a window of mz or retention time values or to retrieve a single point.
    """
    def __init__(self, featureInstance):
        """
        @type featureInstance: parseFeatureXML.Reader
        @param featureInstance: An instance of the parseFeatureXML.Reader class
        """
        self.featureInstance = featureInstance
    
        
    def getFeatures_mzWindow(self, mzStart, mzEnd):
        """
        Get all the features of which the mz value is within mzStart and mzEnd.
        
        @type mzStart: float
        @param mzStart: The lowest m/z value of the window to retrieve features from
        @type mzEnd: float
        @param mzEnd: The highest m/z value of the window to retrieve features from
        @rtype: list
        @return: A list of all the features that have an mz between mzStart and mzEnd
        @raise TypeError: rtStart or rtEnd is not of type int or float
                
        B{Example:}
        
        Print a list of the features that have an m/z between 499.9 and 500:
        
        >>> featureXML = parseFeatureXML.Reader('example_featureXML_file.featureXML')
        >>> featureLocation = getWindow.FeatureLocation(featureXML)
        >>> for feature in featureLocation.getFeatures_mzWindow(499.9,500):
        ...    print feature
        <Element 'feature' at 0xc4d5e10>
        <Element 'feature' at 0xc4ca8a0>
        <Element 'feature' at 0xc4cf210>
        """ 
        if not isinstance(mzStart, int) and not isinstance(mzStart, float):
            raise TypeError, 'mzStart has to be of type int or float. Instead, is of type: '+str(type(mzStart))
        if not isinstance(mzEnd, int) and not isinstance(mzEnd, float):
            raise TypeError, 'mzEnd has to be of type int or float. Instead, is of type: '+str(type(mzEnd))
        
        for feature in self.featureInstance.getSimpleFeatureInfo():
            if mzStart <= float(self.featureInstance['mz']) <= mzEnd:
                # return the feature
                yield feature
                            
    def getFeatures_rtWindow(self, rtStart, rtEnd):
        """
        Get all the features of which the mz value is within mzStart and mzEnd. NOTE: The rt is in seconds !!!
        
        @type rtStart: float
        @param rtStart: The lowest retention time value of the window to retrieve features from
        @type rtEnd: float
        @param rtEnd: The highest retention time value of the window to retrieve features from
        @rtype: list
        @return: A list of all the features that have an rt between rtStart and rtEnd
        @raise TypeError: rtStart or rtEnd is not of type int or float
        
        B{Example:}
        
        Print a list of the features that have a retention time between 450 and 500 B{seconds}
        
        >>> featureXML = parseFeatureXML.Reader('example_featureXML_file.featureXML')
        >>> featureLocation = getWindow.FeatureLocation(featureXML)
        >>> for feature in featureLocation.getFeatures_mzWindow(300,500):
        ...    print feature
        <Element 'feature' at 0xc4d5e10>
        <Element 'feature' at 0xc4ca8a0>
        <Element 'feature' at 0xc4cf210>
        """ 
        if not isinstance(rtStart, int) and not isinstance(rtStart, float):
            raise TypeError, 'rtStart has to be of type int or float. Instead, is of type: '+str(type(rtStart))
        if not isinstance(rtEnd, int) and not isinstance(rtEnd, float):
            raise TypeError, 'rtEnd has to be of type int or float. Instead, is of type: '+str(type(rtEnd))

        for feature in self.featureInstance.getSimpleFeatureInfo():
            # if the rt value is between rtStart and rtEnd
            if rtStart <= self.featureInstance['retention time'] <= rtEnd:
            # return the feature
                yield feature
           

class PeakLocation:
    """
    Several functions to retrieve a list of peaks in a window of mz or retention time values
    """
    def __init__(self, peakInstance):
        """
        @type peakInstance: parsePeaksMzML.Reader
        @param peakInstance: An instance of the parsePeaksMzML.Reader class
        """
        self.peakInstance = peakInstance
        
    def getPeaks_mzWindow(self, mzStart, mzEnd):
        """
        Get all the features of which the mz value is within mzStart and mzEnd.
        
        @type mzStart: float
        @param mzStart: The lowest m/z value of the window to retrieve features from
        @type mzEnd: float
        @param mzEnd: The highest m/z value of the window to retrieve features from
        @rtype: list
        @return: A list of all the features that have an mz between mzStart and mzEnd
        @raise TypeError: rtStart or rtEnd is not of type int
                
        B{Example:}
        
        Print a list of the features that have an m/z between 499.9 and 500:
        
        >>> peaks = parsePeaksMzML.Reader('example_peak_file.peaks.mzML')
        >>> peakLocation = getWindow.PeakLocation(peaks)
        >>> for peak in peakLocation.getPeaks_mzWindow(350,500):
        ...     print peak
        <Element '{http://psi.hupo.org/ms/mzml}spectrum' at 0xbdbbc90>
        <Element '{http://psi.hupo.org/ms/mzml}spectrum' at 0xbdca120>
        <Element '{http://psi.hupo.org/ms/mzml}spectrum' at 0xbdcd3c0>
        """ 
        if not isinstance(mzStart, int) and not isinstance(mzStart, float):
            raise TypeError, 'mzStart has to be of type int or float. Instead, is of type: '+str(type(mzStart))
        if not isinstance(mzEnd, int) and not isinstance(mzEnd, float):
            raise TypeError, 'mzEnd has to be of type int or float. Instead, is of type: '+str(type(mzEnd))
        
        for peak in self.peakInstance.getSimpleSpectraInfo():
            # if the base peak m/z is in the range aappend it to peakList
            if mzStart <= float(self.peakInstance['base peak m/z']) <= mzEnd:
            # return the feature
                yield peak
    
    def getPeaks_rtWindow(self, rtStart, rtEnd):
        """
        Get all the features of which the mz value is within mzStart and mzEnd. NOTE: The rt is in seconds !!!
        
        @type rtStart: float
        @param rtStart: The lowest retention time value of the window to retrieve features from
        @type rtEnd: float
        @param rtEnd: The highest retention time value of the window to retrieve features from
        @rtype: list
        @return: A list of all the features that have an rt between rtStart and rtEnd
        @raise TypeError: rtStart or rtEnd is not of type int
        
        B{Example:}
        
        Print a list of the features that have a retention time between 450 and 500 B{seconds}
        
        >>> peaks = parsePeaksMzML.Reader('example_peak_file.peaks.mzML')
        >>> peakLocation = getWindow.PeakLocation(peaks)
        >>> for peak in peakLocation.getPeaks_rtWindow(500,3000):
        ...    print peak
        <Element '{http://psi.hupo.org/ms/mzml}spectrum' at 0x10c2d810>
        <Element '{http://psi.hupo.org/ms/mzml}spectrum' at 0x10c28900>
        <Element '{http://psi.hupo.org/ms/mzml}spectrum' at 0x10c28450>
        <Element '{http://psi.hupo.org/ms/mzml}spectrum' at 0x10c272a0>
        """ 
        if not isinstance(rtStart, int) and not isinstance(rtStart, float):
            raise TypeError, 'rtStart has to be of type int or float. Instead, is of type: '+str(type(rtStart))
        if not isinstance(rtEnd, int) and not isinstance(rtEnd, float):
            raise TypeError, 'rtEnd has to be of type int or float. Instead, is of type: '+str(type(rtEnd))
        
        for peak in self.peakInstance.getSimpleSpectraInfo():
            # if the rt value is between rtStart and rtEnd
            if rtStart <= float(self.peakInstance['scan start time'])*60 <= rtEnd:
                # return the feature
                yield peak
                            

                
                
class SpectraLocation:  
    """
    Several functions to retrieve a list of spectra in a window of mz or retention time values
    """
    def __init__(self, mzmlInstance):
        """
        @type peakInstance: pymzml.run.Reader
        @param peakInstance: An instance of the pymzml.run.Reader class
        """
        self.mzmlInstance = mzmlInstance          
        # a list of copies of the spectrum in case function is called more than once   
        self.spectraList = []
        
    def getSpectra_mzWindow(self, mzStart, mzEnd):
        """
        Get all the spectra of which the mz value is within mzStart and mzEnd.
        
        @type mzStart: float
        @param mzStart: The lowest mz value of the window to retrieve spectra from
        @type mzEnd: float
        @param mzEnd: The highest mz value of the window to retrieve spectra from
        @rtype: list
        @return: A list of all the spectra that have an mz between mzStart and mzEnd
        @raise TypeError: rtStart or rtEnd is not of type int
                
        B{Example:}
        
        Print a list of the spectra that have an m/z between 400 and 500:
        
        >>> import pymzml
        >>> spectra = pymzml.run.Reader('example_featureXML_file.featureXML')
        >>> spectrumLocation = getWindow.SpectraLocation(spectra)
        >>> for spectrum in spectrumLocation.getSpectra_mzWindow(400, 500):
        ...    print spectrum['id']
        1
        19
        51
        """ 
        if not isinstance(mzStart, int) and not isinstance(mzStart, float):
            raise TypeError, 'mzStart has to be of type int or float. Instead, is of type: '+str(type(mzStart))
        if not isinstance(mzEnd, int) and not isinstance(mzEnd, float):
            raise TypeError, 'mzEnd has to be of type int or float. Instead, is of type: '+str(type(mzEnd))

        
        if self.spectraList:
            for spectrum in self.spectraList:
                # a list of tuples with each tuple having (m/z, intensity)
                mz = spectrum.mz
                intensity = spectrum.i

                # for explanation why/hower lowerIndex and upperIndex is done, read comments in the else statement 
                lowerIndex = bisect.bisect_left(mz, mzStart)
                upperIndex = bisect.bisect_right(mz, mzEnd)
                
                for index in range(lowerIndex, upperIndex):
                    # the [index] is to get the right tuple out of peakList, the [0] is to get the m/z value out of the peak tuple
                    if mzStart <= float(mz[index]) <= mzEnd:
                        # yield the spectrum
                        yield spectrum, intensity[index]
        else:
            time0 = time.time()
            for spectrum in self.mzmlInstance:
                # makes function a bit slower, but this is necesarry in case any function from SpectraLocation gets called
                # again because you can only loop through the mzml instance once (because it is a generator object)
                self.spectraList.append(copy.deepcopy(spectrum))
                
                mz = spectrum.mz
                intensity = spectrum.i

                # use bisect to get the list index where lower and higher bound is, then use that index to loop through the list
                # for only that particular part and get the right slice.
                # bisect_left finds the leftmost value, so if there happen to be 2 m/z of the same value (dont know if that's possible) it gets the left most
                # it doesn't have to be the exact number, it rounds up, so if mzStart = 340, and you have 339 and 341, it gives the index for 341
                # The (mzStart,) part makes it a tuple with 1 value. This makes it search on the first value of the peak tuple                
                lowerIndex = bisect.bisect_left(mz, mzStart)
                
                # bisect.bisect_right gives the right most index (see 4 lines up for more info). The -1 at index is to make it round down. Example,
                # if mzEnd = 340 and you have 339 and 341, the index would be that of 341. But because 340 is the upper limit, we want the index of
                # 339. So -1 to the index.
                # upperIndex is rounded up, but because it's used in range, which works with < instead of =< this works.
                upperIndex = bisect.bisect_right(mz, mzEnd)
                
                for index in range(lowerIndex, upperIndex):
                    # the [index] is to get the right tuple out of peakList, the [0] is to get the m/z value out of the peak tuple
                    if mzStart <= float(mz[index]) <= mzEnd:
                        # yield the spectrum
                        yield spectrum, intensity[index]
        print 'done mzStart mzEnd between: ',mzStart, mzEnd
        
        
    def getSpectra_rtWindow(self, rtStart, rtEnd):
        """
        Get all the features of which the retention time value is within rtStart and rtEnd.
        The retention time is in seconds (in the .mzml file it stands as minutes)
        
        @type rtStart: float
        @param rtStart: The lowest number of the window to retrieve spectra from
        @type rtEnd: float
        @param rtEnd: The highest number of the window to retrieve spectra from
        @rtype: list
        @return: A list of all the spectra that have an mz between mzStart and mzEnd
        @raise TypeError: rtStart or rtEnd is not of type int
                
        B{Example:}
        
        Print a list of the spectra that have an retention time (in seconds) between 400 and 500:
        
        >>> import pymzml
        >>> spectra = pymzml.run.Reader('example_featureXML_file.featureXML')
        >>> spectrumLocation = getWindow.SpectraLocation(spectra)
        >>> for spectrum in spectrumLocation.getSpectra_rtWindow(400, 500):
        ...    print spectrum['id']
        19
        """ 
        if not isinstance(rtStart, int) and not isinstance(rtStart, float):
            raise TypeError, 'rtStart has to be of type int or float. Instead, is of type: '+str(type(rtStart))
        if not isinstance(rtEnd, int) and not isinstance(rtEnd, float):
            raise TypeError, 'rtEnd has to be of type int or float. Instead, is of type: '+str(type(rtEnd))

        if self.spectraList:
            for spectrum in spectraList:
                # loop through all the peaks
                for peak in spectrum.peaks:
                    if mzStart <= float(peak[0]) <= mzEnd:
                        # return the spectrum
                        yield spectrum, peak
        else:       
            for spectrum in self.mzmlInstance:
                # makes function a bit slower, but this is necesarry in case any function from SpectraLocation gets called
                # again because you can only loop through the mzml instance once (because it is a generator object)
                self.spectraList.append(copy.deepcopy(spectrum))
                if str(spectrum['id']).lower() == 'tic' or str(spectrum['id']).lower() == 'sic':
                    continue
                # its scan start time * 60 because scan start time is in minutes, I want to keep everything to seconds
                if rtStart <= float(spectrum['scan time'])*60 <= rtEnd:
                    # return the spectrum
                    yield spectrum