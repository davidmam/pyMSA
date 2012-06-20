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
Comparing how alike two MS runs are by using pymzml's compareSpectra.
"""

# author: ndeklein
# date:20/03/2012
# summary: Comparing how alike two runs are by using pymzml's compareSpectra.
import sys
# to be able to import pymzml from a locally installed pymzml   * REMOVE WHEN SENDING TO OTHER USERS *
try:
    sys.path.append('/homes/ndeklein/python2.6/site-packages')
except:
    pass

import rpy2.robjects as R
import rPlotGenerics as rPlots
import gc
import time
import copy
import pymzml

class CompareRuns:
    """
    Class that compares multiple runs with each other. Can compare mzML (later on also peaks.mzML and featureXML files).
    """
    def __init__(self, *args):
        """
        @param args: n amount of pymzml.run.Reader instances to be compared. Need to be at least 2. 
        @rtype: unknown
        @return: unknown
        @raise TypeError: Not enough arguments given to compareMzml
        @raise TypeError: At least on of the arguments given to CompareRuns is not of type pymzml.run.Reader
        """
        if len(args) < 2:
            raise TypeError, 'compareMzml expects at least 2 arguments. '+str(len(args))+' argument(s) given'
        
        self.msrunList = []
        # disable garbage collection. appending instances to a list goes faster this way  
        gc.disable()
        for arg in args:
            spectrumList = []
            if not isinstance(arg, pymzml.run.Reader):
                # arg has to be of type pymzml.run.Reader
                raise TypeError, 'At least one of the arguments given to CompareRuns was not of type pymzml.run.Reader. Instead, was of type: '+str(type(arg))
            # because each spectrum is needed more than once, but looping through the spectrums makes them unable to be used again, each spectrum has to be copied.
            # It's easier to do that now once, otherwise it has to be done multiple times later on.         
            for spectrum in arg:
                # need to make a copy of the spectra, otherwise it keeps given same memory location
                spectrumList.append(copy.deepcopy(spectrum))
            self.msrunList.append(spectrumList)
      # enable darbage collection again, don't want to clog up the memory
        gc.enable()
                
    def compare_mzML(self):
        """
        Comparing how alike two MS runs are by using pymzml's compareSpectra. 
        The MS runs should be parsed by pymzml's pymzml.run.Reader (this is validated in __init__ of CompareRuns).
        
        @rtype: List, numeric, numeric
        @return: A list of the similarity scores of all the compared spectra, the amount of spectra that aren't used from msrun1 and the amount of spectra that aren't used of msrun2
        
        B{Example:}
        
        Comparing two msruns and plotting a histogram of the similarity between the spectra
    
        >>> from pyMS import compareRuns
        >>> import pymzml
        >>> msrun1 = pymzml.run.Reader(r'example_files/input/example_aligned_file_1.aligned.mzML')
        >>> msrun2 = pymzml.run.Reader(r'example_files/input/example_aligned_file_2.aligned.mzML')
        >>> compare = compareRuns.CompareRuns(msrun1, msrun2)
        >>> similarityList, missCount1, missCount2 = compare.compare_mzML()
        >>> floatVector = R.FloatVector(similarityList)
        >>> plots = rPlots.Plots()
        >>> plots.histogram('example_files/output/similarity_histogram.png', floatVector, title='compare example 1 and example 2. Missed in first: '+str(missCount1)+' missed in second: '+str(missCount2), 
                                xlab='similarity', ylab='# of spectra')
        """
        # the i and y loop make sure that every msrun is compared to every other msrun. For example, if there are 3 msruns given
        # this gives for i == 0, y == 1 2 and 3, for i == 1, y == 2 and 3, and for i == 2, y == 3
        
        # disable garbage collection. appending instances to a list goes faster this way  
        gc.disable()
        for i in range(len(self.msrunList)-1):
            for y in range(i+1, len(self.msrunList)):
                # counter of the amount of spectra missed
                missCount1 = 0
                missCount2 = 0
                # spectrum counter to keep track of the spectrum number x is currently at
                specCount1 = 0
                specCount2 = 0

                # a list to keep track of the similarities between the spectras in both msruns
                similarityList = []
                
                for spectrum in self.msrunList[i]:
                    # make sure there is no index out of bounds error
                    if specCount1 < len(self.msrunList[i]) and specCount2 < len(self.msrunList[y]):
                        if self.msrunList[i][specCount1]['id'] == 'TIC' or self.msrunList[y][specCount2]['id'] == 'TIC':
                            break
                        # as long as the retention time (or scan time) of run 1 and run 2 aren't the same, move the lowest value of the two to the next spectra
                        # untill they are the same. Only do this as long as specCount1 and specCount2 are not higher than the length of run 1 and run 2 respectively
                        while specCount1 < len(self.msrunList[i]) and specCount2 < len(self.msrunList[y]) and self.msrunList[i][specCount1]['id'] != 'TIC' and  self.msrunList[y][specCount2]['id'] != 'TIC'\
                                and round(self.msrunList[i][specCount1]['scan time'],4) != round(self.msrunList[y][specCount2]['scan time'],4):                               
                            if round(self.msrunList[i][specCount1]['scan time'],4) > round(self.msrunList[y][specCount2]['scan time'],4):
                                missCount1 += 1
                                specCount2 += 1
                            elif round(self.msrunList[i][specCount1]['scan time'],4) < round(self.msrunList[y][specCount2]['scan time'],4):
                                missCount2 += 1
                                specCount1 += 1

                        # Calculates the similarity between every spectrum of the msrun located at the 'ith' position of msrunList
                        # with the spectrum with the same index number of the msrun at the 'yth' position of msrunList
                        if specCount1 < len(self.msrunList[i]) and specCount2 < len(self.msrunList[y]):
                            similarityList.append(self.msrunList[i][specCount1].similarityTo(self.msrunList[y][specCount2]))
                        specCount1 += 1
                        specCount2 += 1

                        
 #                    
#      # enable darbage collection again, don't want to clog up the memory
        gc.enable()
        return similarityList, missCount1, missCount2
       



