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
Example how to compare two (or more) msruns
"""

# author: ndeklein
# date:30/03/2012
# summary: Example how to compare two (or more) msruns

import sys

# for me, PyMSA_dev is not in my default python path
try:
    sys.path.append('/homes/ndeklein/workspace/MS/Trunk/PyMSA_dev')
except:
    pass

from pyMSA import compareRuns
import pymzml
import rpy2.robjects as R
from pyMSA import rPlotGenerics as rPlots

def compare_msrun():
    """
    Example how to compare two runs and plot a histogram of the similarity of all the matching spectra. It can compare
    any two mzML files but works best when comparing two aligned files. It compares the retention time of all the spectra
    of both msruns with each other and when they are the same, uses pymzml's spec1.similarityTo(spec2) function. This returns
    a value between 0-1 for each compared spectrum which can then be plotted. 
    Also possible is to put in 3 or more msrun files, this will compare all msruns with eachother (so: 1 to 2, 1 to 3 and 2 to 3.) 
    
    
    This example script uses the following classes and functions:
      - L{compareRuns.CompareRuns}
      - L{compareRuns.CompareRuns.compare_mzML}

    
    Comparing two msruns and plotting a histogram of the similarity between the spectra
    
    >>> from pyMSA import compareRuns                                    
    >>> import pymzml
    >>> msrun1 = pymzml.run.Reader(r'example_files/input/example_aligned_file_1.aligned.mzML')                                    # Make an instance of pymzml.run.Reader with file you want to compare as input
    >>> msrun2 = pymzml.run.Reader(r'example_files/input/example_aligned_file_2.aligned.mzML')                                    # Make another instance of pymzml.run.Reader with file you want to compare as input
    >>> compare = compareRuns.CompareRuns(msrun1, msrun2)                                                                         # Make an instance of compareRuns.CompareRuns with the two instances of pymzml.run.Reader that you want to compare
    >>> similarityList, missCount1, missCount2 = compare.compare_mzML()                                                           # Compare the two files and retrieve a list of similarities
    >>> floatVector = R.FloatVector(similarityList)                                                                               # Make a FloatVector out of the list
    >>> plots = rPlots.Plots()                                                                                                    # Make an instance of rPlots.Plots
    >>> plots.histogram('example_files/output/similarity_histogram.png', floatVector,                                             # Plot a histogram of the results
    ...     xlab='similarity', ylab='# of spectra', width=600, height=600, 
    ...     title='compare example 1 and example 2. Missed in first: '+str(missCount1)+' missed in second: '+str(missCount2))
    """
    
    # Make an instance of pymzml.run.Reader with file you want to compare as input
    msrun1 = pymzml.run.Reader(r'example_files/input/example_aligned_file_1.aligned.mzML')
    # Make another instance of pymzml.run.Reader with file you want to compare as input
    msrun2 = pymzml.run.Reader(r'example_files/input/example_aligned_file_2.aligned.mzML')

    # Make an instance of compareRuns.CompareRuns with the two instances of pymzml.run.Reader that you want to compare
    compare = compareRuns.CompareRuns(msrun1, msrun2)
    # Compare the two files and retrieve a list of similarities
    similarityList, missCount1, missCount2 = compare.compare_mzML()
    # Make a FloatVector out of the list
    floatVector = R.FloatVector(similarityList)
    # Make an instance of rPlots.Plots
    plots = rPlots.Plots()
    # Plot a histogram of the results. Width and height is set to 600 because the title is quite long and it doesn't fit on the default (300 by 300)
    plots.histogram('example_files/output/similarity_histogram.png', floatVector, xlab='similarity', ylab='# of spectra', width=600, height=600, 
                        title='compare example 1 and example 2. Missed in first: '+str(missCount1)+' missed in second: '+str(missCount2))
                                



if __name__ == '__main__':
    compare_msrun()