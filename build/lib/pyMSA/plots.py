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
Different plot functions. 
"""

# author: ndeklein
# date:08/02/2012
# summary: Different plot functions. 

import getWindow
import pymzml
import elementFunctions
import rPlotGenerics
import rpy2.robjects as R
import collections
import mzmlFunctions
import rPlotGenerics

def massWindow_XIC_plot(retentionList, intensityList, outpath='XIC_plot.png', title='XIC_plot', xlab='retention time (seconds)', ylab='summed intensity', extra_arguments={'type':'l'}):
    """
    Plot XIC for a mass window (aggregated) against run time. 
    
    Essentially you are taking the area under the intensity-m/z curve as the single intensity point.

    @type retentionList: list
    @param retentionList: Sorted list of the retention times corresponding to the intensities in intensityList. 
    @type intensityList: list
    @param intensityList: Sorted list of intensities correpsonding to the retention times in retentionList
    @type outpath: string
    @param outpath: The path and name of the file to write out (default = XIC_plot.png)
    @type title: string
    @param title: Title for the plot (default = XIC_plot)
    @type xlab: string
    @param xlab: Description of the x-axis of the plot (default = retention time (seconds))
    @type ylab: string
    @param ylab: Description of the y-axis of the plot (default = retention time (seconds))
    @type extra_arguments: dict
    @param extra_arguments: extra arguments to give to the plot, with as key the argument name and value the argument value (can use all the R arguments [see http://stat.ethz.ch/R-manual/R-devel/library/graphics/html/plot.html]). (default = {'type':'l'})
    @raise TypeError: intensityDict or extraArguments not a dict and/or outpath, title, xlab, ylab not a string   

    {Example:}
    
    Plot XIC plot with m/z between 450-452
    
    >>> import pymzml
    >>> import mzmlFunctions
    >>> mzmlInstance = pymzml.run.Reader('example_file.mzML')
    >>> intensityFromSpectra = mzmlFunctions.IntensityFromSpectra(mzmlInstance)
    >>> retentionList, intensityList = intensityFromSpectra.getIntensityFromMZwindow(450, 452)
    >>> massWindow_XIC_plot(retentionList, intensityList)
    """
    if not isinstance(retentionList, list):
        raise TypeError, 'retentionList given to massWindow_XIC_plot is not of type list. Instead, is of type: '+str(type(retentionList))
    if not isinstance(intensityList, list):
        raise TypeError, 'intensityList given to massWindow_XIC_plot is not of type list. Instead, is of type: '+str(type(intensityList))
    if not isinstance(extra_arguments, dict):
        raise TypeError, 'extra_arguments given to massWindow_XIC_plot is not of type dict. Instead, is of type: '+str(type(extra_arguments))
    if not isinstance(outpath, str):
        raise TypeError, 'outpath given to outpath is not of type str. Instead, is of type: '+str(type(outpath))
    if not isinstance(title, str):
        raise TypeError, 'title given to outpath is not of type str. Instead, is of type: '+str(type(title))
    if not isinstance(xlab, str):
        raise TypeError, 'xlab given to outpath is not of type str. Instead, is of type: '+str(type(xlab))
    if not isinstance(ylab, str):
        raise TypeError, 'ylab given to outpath is not of type str. Instead, is of type: '+str(type(ylab))
    
      
    retentionTimeVector = R.FloatVector(retentionList)
    # loop through the sorted keys to get sorted intensities
    intensityVector = R.FloatVector(intensityList)
    
    plots = rPlotGenerics.Plots()
    plots.plot(outpath, retentionTimeVector, intensityVector, title=title, xlab=xlab, ylab=ylab, plotArgs = extra_arguments)
    
    
def parent_to_XIC_plot(mzmlInstance, parentMass, maxCharge=4, outpath='XIC_plot.png', title='XIC_plot', xlab='retention time (seconds)', ylab='summed intensity', extra_arguments={'type':'l'}):
    """
    Makes an XIC overlapping plot of all the charge variations of the parentving the sum and RT as the y and X point respectively for the plot.
    mass, up to the charge given to maxCharge.
    E.g., if you run parent_to_XIC_plot(1200, 4), this will plot the XIC for 600 (2+), 400 (3+) and 300 (4+).
    
    @type mzmlInstance: pymzml.run.Reader
    @param mzmlInstance: Instance of pymzml.run.Reader class which you want to use to plot the XIC from
    @type parentMass: Number
    @param parentMass: The mass of the peptide you want the different charge plots to be made from.
    @type maxCharge: Number
    @type outpath: string
    @param outpath: The path and name of the file to write out (default = XIC_plot.png)
    @type title: string
    @param title: Title for the plot (default = XIC_plot)
    @type xlab: string
    @param xlab: Description of the x-axis of the plot (default = retention time (seconds))
    @type ylab: string
    @param ylab: Description of the y-axis of the plot (default = retention time (seconds))
    @type extra_arguments: dict
    @param extra_arguments: extra arguments to give to the plot, with as key the argument name and value the argument value (can use all the R arguments [see http://stat.ethz.ch/R-manual/R-devel/library/graphics/html/plot.html]). (default = {'type':'l'})
    @param maxCharge: The maximum z charge to calculate the m/z for. (default=4)
    @raise TypeError: intensityDict or extraArguments not of tpye dict and/or outpath, title, xlab, ylab not a string and/or parentMass and maxCharge not of type int and/or mzmlInstance not of type pymzml.run.Reader 
    @raise RuntimeError: maxCharge has to be 2 or higher
    
    B{Example:}

    Plot all peptides with charge 2-4 for mother peptide weight 1500
    
    >>> import pymzml
    >>> mzmlInstance = pymzml.run.Reader('example_file.mzML')
    >>> parent_to_XIC_plot(mzmlInstance, 1500)                    #runs with default charge 2-4, outputs to XIC_plot 
    """
    if not isinstance(mzmlInstance, pymzml.run.Reader):
        raise TypeError, 'mzmlInstance given to massWindow_XIC_plot is not of type pymzml.run.Reader(). Instead, is of type: '+str(type(mzmlInstance))
    if not isinstance(parentMass, int) and not isinstance(parentMass, float):
        raise TypeError, 'parentMass given to parent_to_XIC_plot is not of type int or float. Instead, is of type: '+str(type(parentMass))
    if not isinstance(maxCharge, int) and not isinstance(maxCharge, float):
        raise TypeError, 'maxCharge given to parent_to_XIC_plot is not of type int or float. Instead, is of type: '+str(type(maxCharge))
    if not maxCharge >= 2:
        raise RuntimeError, 'maxCharge given to parent_to_XIC_plot has to be >= 2. It was: '+str(maxCharge)
    if not isinstance(extra_arguments, dict):
        raise TypeError, 'extra_arguments given to massWindow_XIC_plot is not of type dict. Instead, is of type: '+str(type(extra_arguments))
    if not isinstance(outpath, str):
        raise TypeError, 'outpath given to outpath is not of type str. Instead, is of type: '+str(type(outpath))
    if not isinstance(title, str):
        raise TypeError, 'title given to outpath is not of type str. Instead, is of type: '+str(type(title))
    if not isinstance(xlab, str):
        raise TypeError, 'xlab given to outpath is not of type str. Instead, is of type: '+str(type(xlab))
    if not isinstance(ylab, str):
        raise TypeError, 'ylab given to outpath is not of type str. Instead, is of type: '+str(type(ylab))
    
    # count to know which is the first plot to make (because that uses plot(), the rest uses lineS()
    retentionCount = 1
    # open the png
    R.r.png(outpath, width=600, height=600)
    intensityFromSpectra = mzmlFunctions.IntensityFromSpectra(mzmlInstance)
    # list of colors to use for plotting
    colorList = ['blue','red', 'yellow', 'green']
    for charge in range(maxCharge, 1, -1):
        lowerBound = (parentMass)/charge
        upperBound = (parentMass)/charge
        plots = rPlotGenerics.Plots()
        color = R.r['rgb'](**plots.getColor(colorList[charge-2]))
        try:
            retentionList, intensityList = intensityFromSpectra.getIntensityFromMZwindow(lowerBound, upperBound)
            retentionVector = R.FloatVector(retentionList)
            intensityVector = R.FloatVector(intensityList)
            if retentionCount == 1:
                R.r['plot'](retentionVector, intensityVector, main=title, xlab=xlab, ylab=ylab, col=color, **extra_arguments)
            else:
                R.r['lines'](retentionVector, intensityVector, col=color)
            retentionCount += 1
        except RuntimeError:
            print 'no spectrums found with m/z between '+str(lowerBound)+' and '+str(upperBound)
        print 'done charge: ', charge
        