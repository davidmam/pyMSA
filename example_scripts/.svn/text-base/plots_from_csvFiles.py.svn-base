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
Examples of how to make different kinds of plots from csv data files 
"""
# author: ndeklein
# date:20/03/2012
# summary: Different ways of plotting information

# to be able to import pyMSA and without making a package (because info changes everytime during development, don't want to make a new
# package everytime) 
import sys

# for me, PyMSA_dev is not in my default python path
try:
    sys.path.append('/homes/ndeklein/workspace/MS/Trunk/PyMSA_dev')
except:
    pass
from pyMSA import rFunctions
from pyMSA import rPlotGenerics as rPlots
import rpy2.robjects as R



def feature_per_intensity_histogram():
    """
    Example of how to make a histogram of the features per intensity.
    
    Takes a csv file which contains information on all the features. The important information are the intensities. Because every row is one feature, to get the features
    per intensity it is possible to count the occurence of each intensity. It makes a vector out of all the intensities per feature in example_files/input/feature.csv.
    It retrieves vectors of information about the feature, so with little tweaking this method can be used any time that you can make a vector out 
    of your data. For better viewing the data is logged with base 10.
    
    This example script uses the following functions:
      - L{rFunctions.readCsvFile}
      - L{rFunctions.getRowsWithUniqColumn}
      - L{rFunctions.index}
      - L{rFunctions.takeLog}
      - L{rPlots.Plots.histogram}
    
      
    >>> from pyMSA import rFunctions
    >>> from pyMSA import rPlots
    >>> featDataframe = rFunctions.readCsvFile('example_files/input/feature.csv')                                                    # Read a csv file into a rpy2 dataframe with featurs and intensities
    >>> featDataframeUniq = rFunctions.getRowsWithUniqColumn(featDataframe, 'id')                                                    # Remove the rows with redundant id's from featDataframe
    >>> featIntensityVector = featDataframe[rFunctions.index(featDataframeUniq, 'intensity')]                                        # Retrieve a vector of intensities from the unique features
    >>> featLogIntensityVector = rFunctions.takeLog(featIntensityVector,10)                                                          # Take the logarithm of all the values in the vector with base 10
    >>> rplots = rPlots.Plots()                                                                                                      # Instantiate rPlots.Plots()
    >>> plots.histogram('example_files/output/feature_per_intensity_histogram.png', featLogIntensityVector, width=400, height=400,   # draw a plot with 1 histogram
                                        title='#features per intensity',  ylab = '# of features', xlab = 'intensity')
    """
    # Reading in a csv file, seperated by tabs into a dataFrame. A feature.csv file contains at least a column 'id' with the id's of all features and a columne
    # 'intensity' with the intensity of each feature. A file that is separated by a different delimiter can be given using the
    # sep argument. So rFunctions.readCsvFile('example_files/input/feature.csv', sep=',') would separate on commas. Additional arguments can be found in the
    # documentation of rFunctions.readCsvFile()
    featDataframe = rFunctions.readCsvFile('example_files/input/feature.csv')
    
    # Remove all the rows from featDataframe of which the value in the column 'id' already exists. featDataframeUniq is a sub-dataframe of
    # featDataframe with only rows with unique id's.  
    featDataframeUniq = rFunctions.getRowsWithUniqColumn(featDataframe, 'id')
        
    # Retreive all the values of the column 'intensity' from featDataframeUniq and return them as a vector. The vector featIntensityVector conatains
    # the intensities of all the unique feature id's. 
    featIntensityVector = featDataframe[rFunctions.index(featDataframeUniq, 'intensity')]
    
    # Take the log with base 10 of all the values in featIntensityVector.
    featLogIntensityVector = rFunctions.takeLog(featIntensityVector,10)

    # make an instance of rPlots.Plots()
    plots = rPlots.Plots()
    
    # using rplots.histogram to plot a histogram. First argument is the outfile, second argument is the vector for the histogram,
    # title is the title of the graph, xlab is the description that will go under the x-axis, # y-lab is the description that will go to the y-axis.
    # The first 3 positional arguments are mandatory, the keyworded arguments are given to the **kwargs of histogram and are optional. 
    # For more possible arguments see the rPlots.Plots.histogram documentation 
    plots.histogram('example_files/output/feature_per_intensity_histogram.png', featLogIntensityVector, width=400, height=400, 
                                        title='#features per intensity',  ylab = '# of features', xlab = 'intensity')


def msms_per_intensity_histogram():
    """
    Example of how to make a histogram of the MS/MS per intensity.
    
    Takes a csv file of spectra with a column 'ms level' and a column with the base peak intensity. It makes a vector out of all the intensities per spectrum in 
    example_files/input/mzml.csv. It retrieves vectors of information about the intensities, so with little tweaking this method can be used any time that you can 
    make a vector out of your data.
    
    This example script uses the following functions:
      - L{rFunctions.readCsvFile}
      - L{rFunctions.index}
      - L{rPlots.Plots.barplot}
      - L{rFunctions.takeLog}

       
    >>> from pyMSA import rFunctions
    >>> from pyMSA import rPlots
    >>> mzmlDataframe = rFunctions.readCsvFile('example_files/input/mzML.csv')                                                       # Read a csv file into a rpy2 dataframe with precursors and intensities
    >>> precursorDataframe = mzmlDataframe.rx(mzmlDataframe[rFunctions.index(mzmlDataframe, 'ms.level')].ro >= 2, True)              # Retrieve a subset dataframe of mzmlDataframe where values in column 'ms level' >= 2
    >>> intensityVector = precursorDataframe[rFunctions.index(precursorDataframe, 'base.peak.intensity')]                            # Retrieve a vector all the values from the 'base peak intensity' column
    >>> logIntensityVector = rFunctions.takeLog(intensityVector, 10                                                                  # Take the log10 of all the values in the intensityVector
    >>> rplots = rPlots.Plots()                                                                                                      # Instantiate rPlots.Plots()
    >>> plots.barplot('example_files/output/msms_per_feature_barplot.png', precursorTable, width=400, height=400,                     # draw a histogram
                        title='#MS/MS per feature', xlab = '# features', ylab = '# MS/MS')
 
    """
    # Reading in a csv file, seperated by tabs into a dataFrame. A feature.csv file contains at least a column 'id' with the id's of all features and a columne
    # 'intensity' with the intensity of each feature. A file that is separated by a different delimiter can be given using the
    # sep argument. So rFunctions.readCsvFile('example_files/input/mzML.csv', sep=',') would separate on commas. Additional arguments can be found in the
    # documentation of rFunctions.readCsvFile()
    mzmlDataframe = rFunctions.readCsvFile('example_files/input/mzML.csv', head=True, sep='\t', na='N/A')
    
    # Get a subset of csvData with only rows that have a value of 2 or higher in the 'ms level' column (the rows that have an MS/MS precursor)
    # mzmlDataframe.rx and the .ro at the are rpy2 functions. It is possible to use these because csvData is a rpy2.robjects.DataFrame object.
    # The rFunctions.index() is used because, although R allows getting a column by name, rpy2 only allows getting columns by number.
    # rFunctions.index(csvData,'ms.level') returns the number of the 'ms level' column (rpy2 makes a '.' out of spaces).
    # The same would have been: mzmlDataframe.rx(mzmlDataframe[0].ro >= 2, True), if 'ms level' is the first column of csvData.
    precursorDataframe = mzmlDataframe.rx(mzmlDataframe[rFunctions.index(mzmlDataframe, 'ms.level')].ro >= 2, True)
    
    # Retrieve all the values of the column 'base.peak.intensity' from precursorDataframe and return them as a vector. The vector precursorDataframe 
    # contains the intensities of all the unique MS/MS precursors (because in the previous step only 'ms level' >= 2 retrieved)
    intensityVector = precursorDataframe[rFunctions.index(precursorDataframe, 'base.peak.intensity')]
    
    # Take the log with base 10 of all the values in intensityVector
    logIntensityVector = rFunctions.takeLog(intensityVector, 10)
    
    # make an instance of rPlots.Plots()
    plots = rPlots.Plots()

    # using rplots.histogram to plot a histogram. First argument is the outfile, second argument is the vector for the histogram,
    # title is the title of the graph, xlab is the description that will go under the x-axis, y-lab is the description that will go to the y-axis.
    # The first 3 positional arguments are mandatory, the keyworded arguments are given to the **kwargs of histogram and are optional. 
    # For more possible arguments see the rPlots.Plots.histogram documentation 
    plots.histogram('example_files/output/msms_per_intensity_histogram.png', logIntensityVector, width=400, height=400, title='test #features per intensity',  
                            xlab = 'log10 of intensity', ylab = '# of test features')


def msms_and_spectrum_per_ioncurrent_histogram():
    """
    Example of how to make a histogram of the ion current per ms level (1 and 2).
    
    Takes a mzml.csv file. It makes a vector out of all the total ion currents per spectrum in example_files/input/mzml.csv. It retrieves vectors of information 
    about the spectra, so with little tweaking this method can be used any time that you can make a vector out of your data. For better viewing the data is logged 
    with base 10.
    
    This example script uses the following functions:
      - L{rFunctions.readCsvFile}
      - L{rFunctions.getRowsWithUniqColumn}
      - L{rFunctions.index}
      - L{rFunctions.takeLog}
      - L{rPlots.Plots.histogram}
    
    
    >>> from pyMSA import rFunctions
    >>> from pyMSA import rPlots
    >>> import rpy2.robjects as R
    >>> mzmlDataframe = rFunctions.readCsvFile('example_files/input/mzML.csv')                                            # Read a csv file into a rpy2 dataframe with precursors and intensities
    >>> precursorDataframe = mzmlDataframe.rx(mzmlDataframe[rFunctions.index(mzmlDataframe, 'ms.level')].ro >= 2, True)   # Retrieve a subset dataframe of mzmlDataframe where values in column 'ms level' >= 2
    >>> precursorDataframe = mzmlDataframe.rx(mzmlDataframe[rFunctions.index(mzmlDataframe, 'ms.level')].ro == 1, True)   # Retrieve a subset dataframe of mzmlDataframe where values in column 'ms level' == 1
    >>> nonPrecursorIoncount = precursorDataframe[rFunctions.index(precursorDataframe, 'total.ion.current')]              # Retrieve a vector of all the data in the column 'total ion current' of precursorDataframe
    >>> nonPrecursorIoncount = nonPrecursorDataframe[rFunctions.index(nonPrecursorDataframe, 'total.ion.current')]        # Retrieve a vector of all the data in the column 'total ion current' of nonPrecursorDataframe
    >>> logPrecursorIoncount = rFunctions.takeLog(precursorIoncount, 10)                                                  # Take the logarithm of all the values in the vector with base 10
    >>> logNonPrecursorIoncount = rFunctions.takeLog(nonPrecursorIoncount, 10)                                            # Take the logarithm of all the values in the vector with base 10
    >>> rplots = rPlots.Plots()                                                                                           # Instantiate rPlots.Plots()
    plots.histogram('example_files/output/msms_and_spectrum_per_ionCurrent_histogram.png', logPrecursorIoncount, 
                    logNonPrecursorIoncount, title='ion current for ms level 1 and ms level 2', 
                    xlab='ion current', ylab='frequency of spectrum or MS/MS precursor', 
                    legend= {'x':'topright','legend':R.StrVector(['ms level 1', 'ms level 2']), 'lty':R.IntVector([1,1]), 
                            'lwd':R.IntVector([2.5,2.5])})

    """
    # Reading in a csv file, seperated by tabs into a dataFrame. The .csv file contains at least a column 'ms level' with ms levels, a column 'id' with the id's of 
    # the spectra and a column 'total ion current' with the base peak intensities. A file that is separated by a different delimiter can be given using the
    # sep argument. So rFunctions.readCsvFile('example_files/input/mzML.csv', sep=',') would separate on commas. Additional arguments can
    # be found in the documentation of rFunctions.readCsvFile().
    mzmlDataframe = rFunctions.readCsvFile('example_files/input/mzML.csv') 

    # Get a subset of mzmlDataframe with only rows that have a value of 2 or higher in the 'ms level' column (the rows that have an MS/MS precursor)
    # mzmlDataframe.rx and the .ro at the are rpy2 functions. It is possible to use these because mzmlDataframe is a rpy2.robjects.DataFrame object.
    # The rFunctions.index() is used because, although R allows getting a column by name, rpy2 only allows getting columns by number.
    # rFunctions.index(mzmlDataframe,'ms.level') returns the number of the 'ms level' column (rpy2 makes a '.' out of spaces).
    # The same would have been: mzmlDataframe.rx(mzmlDataframe[0].ro >= 2, True), if 'ms level' is the first column of mzmlDataframe.
    precursorDataframe = mzmlDataframe.rx(mzmlDataframe[rFunctions.index(mzmlDataframe, 'ms.level')].ro >= 2, True)
   
    # mzmlDataframe.rx and the .ro at the are rpy2 functions. It is possible to use these because mzmlDataframe is a rpy2.robjects.DataFrame object.
    # The rFunctions.index() is used because, although R allows getting a column by name, rpy2 only allows getting columns by number.
    # rFunctions.index(mzmlDataframe,'ms.level') returns the number of the 'ms level' column (rpy2 makes a '.' out of spaces).
    # The same would have been: mzmlDataframe.rx(mzmlDataframe[0].ro == 1, True), if 'ms level' is the first column of mzmlDataframe.
    nonPrecursorDataframe = mzmlDataframe.rx(mzmlDataframe[rFunctions.index(mzmlDataframe, 'ms.level')].ro == 1, True)

    # Retrieve all the values of the column 'total.ion.current' from precursorDataframe and return them as a vector. The vector precursorDataframe 
    # contains the ion currents of all the unique MS/MS precursors
    precursorIoncount = precursorDataframe[rFunctions.index(precursorDataframe, 'total.ion.current')] 

    # Retrieve all the values of the column 'total.ion.current' from precursorDataframe and return them as a vector. The vector precursorDataframe 
    # contains the ion currents of all the unique ms level: 1 precursors
    nonPrecursorIoncount = nonPrecursorDataframe[rFunctions.index(nonPrecursorDataframe, 'total.ion.current')] 

    # Take the log with base 10 of all the values in logPrecursorIoncount.
    logPrecursorIoncount = rFunctions.takeLog(precursorIoncount, 10)
    
    # Take the log with base 10 of all the values in nonPrecursorIoncount.
    logNonPrecursorIoncount = rFunctions.takeLog(nonPrecursorIoncount, 10)

    # make an instance of rPlots.Plots()
    plots = rPlots.Plots()
    
    # using plots.histogram to plot 2 histograms in one figure. First argument is the outfile, second argument is the vector for one of the histograms,
    # third argument is the vector for the second histogram, title is the title of the graph, xlab is the description that will go under the x-axis,
    # y-lab is the description that will go to the y-axis and legend are the arguments given to make the legend. The first 3 positional arguments are 
    # mandatory, the keyworded arguments are given to the **kwargs of histogram and are optional. For more possible arguments see the rPlots.Plots.histogram 
    # documentation and R's ?legend documentation for more arguments to give to legend. 
    plots.histogram('example_files/output/msms_and_spectrum_per_ionCurrent_histogram.png', logPrecursorIoncount, logNonPrecursorIoncount, title='ion current for ms level 1 and ms level 2', 
                    xlab='ion current', ylab='frequency of spectrum or MS/MS precursor', 
                    legend= {'x':'topright','legend':R.StrVector(['ms level 1', 'ms level 2']), 'lty':R.IntVector([1,1]), 'lwd':R.IntVector([2.5,2.5])})




def feature_and_MSMS_per_intensity_histogram():
    """
    Example of how to make an overlapping histogram of the features and MS/MS precursors per intensity.
    
    Takes a feature.csv file and a mzml.csv file. It makes a vector out of all the intensities per feature in example_files/input/feature.csv
    and a vector of all the intensities per spectrums with ms level > 2 in example_files/input/feature.csv. It retrieves vectors of information 
    about the feature and the MS/MS, so with little tweaking this method can be used any time that you can make an n amount of vectors out 
    of your data. For better viewing the data is logged with base 10.
    
    This example script uses the following functions:
      - L{rFunctions.readCsvFile}
      - L{rFunctions.getRowsWithUniqColumn}
      - L{rFunctions.index}
      - L{rFunctions.takeLog}
      - L{rPlots.Plots.histogram}
    
     
    >>> from pyMSA import rFunctions
    >>> from pyMSA import rPlots
    >>> import rpy2.robjects as R
    >>> featDataframe = rFunctions.readCsvFile('example_files/input/feature.csv')                                         # Read a csv file into a rpy2 dataframe with featurs and intensities
    >>> featDataframeUniq = rFunctions.getRowsWithUniqColumn(featDataframe, 'id')                                         # Remove the rows with redundant id's from featDataframe
    >>> featIntensityVector = featDataframe[rFunctions.index(featDataframeUniq, 'intensity')]                             # Retrieve a vector of intensities from the unique features
    >>> featLogIntensityVector = rFunctions.takeLog(featIntensityVector,10)                                               # Take the logarithm of all the values in the vector with base 10
    >>> mzmlDataframe = rFunctions.readCsvFile('example_files/input/mzML.csv')                                            # Read a csv file into a rpy2 dataframe with precursors and intensities
    >>> precursorDataframe = mzmlDataframe.rx(mzmlDataframe[rFunctions.index(mzmlDataframe, 'ms.level')].ro >= 2, True)   # Retrieve a subset dataframe of mzmlDataframe where values in column 'ms level' > 2
    >>> mzmlIntensityVector = precursorDataframe[rFunctions.index(precursorDataframe, 'base.peak.intensity')]             # Retrieve the intensty of all the MS/MS precursors in precursorSubset
    >>> mzmlLogIntensityVector = rFunctions.takeLog(mzmlIntensityVector, 10)                                              # Take the logarithm with base 10 of all the values in mzmlIntensityVector 
    >>> rplots = rPlots.Plots()                                                                                           # Instantiate rPlots.Plots()
    >>> rplots.histogram('example_files/output/feature_and_msms_per_intensity_histogram.png', featLogIntensityVector,     # draw a plot with 2 histograms and a legend
                         mzmlLogIntensityVector, title='feature and MSMS per intensity', xlab='intensity', 
                         ylab='frequency of MS/MS and Intensity', 
                         legend= {'x':'topright','legend':R.StrVector(['features', 'MS/MS precursors']), 
                                  'lty':R.IntVector([1,1]), 'lwd':R.IntVector([2.5,2.5])})
    """

    # Reading in a csv file, seperated by tabs into a dataFrame. A feature.csv file contains at least a column 'id' with the id's of all features and a columne
    # 'intensity' with the intensity of each feature. A file that is separated by a different delimiter can be given using the
    # sep argument. So rFunctions.readCsvFile('example_files/input/feature.csv', sep=',') would separate on commas. Additional arguments can be found in the
    # documentation of rFunctions.readCsvFile()
    featDataframe = rFunctions.readCsvFile('example_files/input/feature.csv')

    # Remove all the rows from featDataframe of which the value in the column 'id' already exists. featDataframeUniq is a sub-dataframe of
    # featDataframe with only rows with unique id's.  
    featDataframeUniq = rFunctions.getRowsWithUniqColumn(featDataframe, 'id')

    # Retreive all the values of the column 'intensity' from featDataframeUniq and return them as a vector. The vector featIntensityVector conatains
    # the intensities of all the unique feature id's. 
    featIntensityVector = featDataframe[rFunctions.index(featDataframeUniq, 'intensity')]
    
    # Take the log with base 10 of all the values in featIntensityVector.
    featLogIntensityVector = rFunctions.takeLog(featIntensityVector,10)
    
    # Reading in a csv file, seperated by tabs into a dataFrame. The .csv file contains at least a column 'ms level' with ms levels, a column 'id' with the id's of 
    # the spectra and a column 'base peak intensities' with the base peak intensities. A file that is separated by a different delimiter can be given using the
    # sep argument. So rFunctions.readCsvFile('example_files/input/mzML.csv', sep=',') would separate on commas. Additional arguments can
    # be found in the documentation of rFunctions.readCsvFile().
    mzmlDataframe = rFunctions.readCsvFile('example_files/input/mzML.csv') 
    
    # Get a subset of mzmlDataframe with only rows that have a value of 2 or higher in the 'ms level' column (the rows that have an MS/MS precursor)
    # mzmlDataframe.rx and the .ro at the are rpy2 functions. It is possible to use these because mzmlDataframe is a rpy2.robjects.DataFrame object.
    # The rFunctions.index() is used because, although R allows getting a column by name, rpy2 only allows getting columns by number.
    # rFunctions.index(mzmlDataframe,'ms.level') returns the number of the 'ms level' column (rpy2 makes a '.' out of spaces).
    # The same would have been: mzmlDataframe.rx(mzmlDataframe[0].ro >= 2, True), if 'ms level' is the first column of mzmlDataframe.
    precursorDataframe = mzmlDataframe.rx(mzmlDataframe[rFunctions.index(mzmlDataframe, 'ms.level')].ro >= 2, True)
    
    # Retrieve all the values of the column 'base.peak.intensity' from precursorDataframe and return them as a vector. The vector precursorDataframe 
    # contains the intensities of all the unique MS/MS precursors (because in the previous step only 'ms level' >= 2 retrieved)
    mzmlIntensityVector = precursorDataframe[rFunctions.index(precursorDataframe, 'base.peak.intensity')]
    
    # Take the log with base 10 of all the values in mzmlIntensityVector
    mzmlLogIntensityVector = rFunctions.takeLog(mzmlIntensityVector, 10)

    # make an instance of rPlots.Plots()
    plots = rPlots.Plots()

    # using plots.histogram to plot 2 histograms in one figure. First argument is the outfile, second argument is the vector for one of the histograms,
    # third argument is the vector for the second histogram, title is the title of the graph, xlab is the description that will go under the x-axis,
    # y-lab is the description that will go to the y-axis and legend are the arguments given to make the legend. The first 3 positional arguments are 
    # mandatory, the keyworded arguments are given to the **kwargs of histogram and are optional. For more possible arguments see the rPlots.Plots.histogram 
    # documentation and R's ?legend documentation for more arguments to give to legend. 
    plots.histogram('example_files/output/feature_and_msms_per_intensity_histogram.png', featLogIntensityVector, mzmlLogIntensityVector, title='feature and MSMS per intensity', 
                    xlab='intensity', ylab='frequency of MS/MS and Intensity', 
                    legend= {'x':'topright','legend':R.StrVector(['features', 'MS/MS precursors']), 'lty':R.IntVector([1,1]), 'lwd':R.IntVector([2.5,2.5])})
    



def msms_per_feature_barplot():
    """
    Example of how to make a barplot of the MS/MS per feature.
    

    
    This example script uses the following functions:
      - L{rFunctions.readCsvFile}
      - L{rFunctions.index}
      - L{rPlots.Plots.barplot}
    
    
    >>> from pyMSA import rFunctions
    >>> from pyMSA import rPlots
    >>> csvData = rFunctions.readCsvFile('example_files/input/feature_precursor.csv', head=True, sep='\t')                           # Read a csv file into a rpy2 dataframe with # MS/MS per feature
    >>> precursorVector = csvData[rFunctions.index(csvData, 'X..precursors')]                                                        # Retrieve a vector of # of precursors for every feature
    >>> precursorTable = R.r['table'](precursorVector)                                                                               # Make a R table out of the precurosVector (needed for the barplot)
    >>> rplots = rPlots.Plots()                                                                                                      # Instantiate rPlots.Plots()
    >>> plots.barplot('example_files/output/msms_per_feature_barplot.png', precursorTable,width=400, height=400,                     # draw a barplot
                        title='#MS/MS per feature', xlab = '# features', ylab = '# MS/MS')
    """
    # Reading in a csv file, seperated by tabs into a dataFrame. A feature_precursor.csv contains at least a column '# precursors' with the amount of precursors
    # that each feature contains. A file that is separated by a different delimiter can be given using the
    # sep argument. So rFunctions.readCsvFile('example_files/input/mzML.csv', sep=',') would separate on commas. Additional arguments can
    # be found in the documentation of rFunctions.readCsvFile().
    csvData = rFunctions.readCsvFile('example_files/input/feature_precursor.csv', head=True, sep='\t')
    
    # Retreive all the values of the column '# precursors' from csvData and return them as a vector. The vector precursorVector contains
    # the # of precursors of all the feature id's. R dataframe translates '#' to 'X.' and ' ' to '.', that's why it looks for the index of X..precursors
    precursorVector = csvData[rFunctions.index(csvData, 'X..precursors')]

    # make a table out of the precursorVector. This automatically puts the # of precursors (0,1,2,3,4 etc) as x-axis label and amount of features that have
    # that # of precursors as the bars
    precursorTable = R.r['table'](precursorVector)

    # make an instance of rPlots.Plots()
    plots = rPlots.Plots()
    
    # using plots.barplot to plot a barplot. First argument is the name and path of the output file. Second argument is a table. This is type rpy2.robjects.vectors.Array.
    # Title is the title of the graph, xlab is the description that will go under the x-axis, y-lab is the description that will go to the y-axis 
    # The first 3 positional arguments are mandatory, the keyworded arguments are given to the **kwargs of barplot and are optional. For more possible arguments 
    # see the rPlots.Plots.barbplot documentation. 
    plots.barplot('example_files/output/msms_per_feature_barplot.png', precursorTable,width=400, height=400, title='#MS/MS per feature', xlab = '# features', ylab = '# MS/MS')



def msms_per_feature_per_intensity_boxplot():
    """
    Example of how to make a boxplot of the # of MS/MS per feature per intensity.
    
    This example script uses the following functions:
      - L{rFunctions.readCsvFile}
      - L{rFunctions.getRowsWithUniqColumn}
      - L{rFunctions.index}
      - L{rFunctions.takeLog}
      - L{rFunctions.getColumns}
      - L{rPlots.Plots.boxplotFormulae}
    
        
    >>> from pyMSA import rFunctions
    >>> from pyMSA import rPlots
    >>> featDataframe = rFunctions.readCsvFile('example_files/input/feature.csv')                                                            # Read a csv file into a rpy2 dataframe with a column containingintensities
    >>> featDataframeUniq = rFunctions.getRowsWithUniqColumn(featDataframe, 'id')                                                            # Remove the rows with redundant id's from featDataframe
    >>> precursorPerFeatureDataframe = rFunctions.readCsvFile('example_files/input/feature_precursor.csv', head=True, sep='\t')              # Read a csv file into a rpy2 dataframe with a column containing # MS/MS per feature
    >>> mergedFeatureDataframe = R.r['merge'](featDataframeUniq, precursorPerFeatureDataframe)                                               # Merge the two dataframes, so that each feature has an intensity and an #MS/MS per feature
    >>> mergedFeatureDataframe[rFunctions.index(mergedFeatureDataframe, 'intensity')] = R.r['round'](rFunctions.takeLog(featDataframeUniq[rFunctions.index(featDataframeUniq, 'intensity')], 10))    # Take the log10 and round all the values in the 'intensity' column
    >>> vector1 = mergedFeatureDataframe[rFunctions.index(mergedFeatureDataframe, 'X..precursors')]                                          # Retrieve a vector of all values in the column '# precursors'
    >>> vector2 = mergedFeatureDataframe[rFunctions.index(mergedFeatureDataframe,'intensity')]                                               # retrieve a vector of all values in the column 'intensity'
    >>> plots = rPlots.Plots()                                                                                                               # instantiate rPlots.PlotS()
    >>> plots.boxplotFormulae('example_files/output/msms_per_feature_per_intensity_boxplot.png', vector1, vector2, mergedFeatureDataframe,   # plot the boxplot
                    title = 'MS/MS per feature per intensity', ylab = '# of MS/MS per feature', xlab = 'Rounded log10 of intensity')
    """

    # Reading in a csv file, seperated by tabs into a dataFrame. A file that is separated by a different delimiter can be given using the
    # sep argument. So rFunctions.readCsvFile'example_files/input/feature.csv', sep=',') would separate on commas. Additional arguments can be found in the
    # documentation of rFunctions.readCsvFile()
    featDataframe = rFunctions.readCsvFile('example_files/input/feature.csv')
    
    # Remove all the rows from featDataframe of which the value in the column 'id' already exists. featDataframeUniq is a sub-dataframe of
    # featDataframe with only rows with unique id's.  
    featDataframeUniq = rFunctions.getRowsWithUniqColumn(featDataframe, 'id')
    
    # Reading in a csv file, seperated by tabs into a dataFrame. A file that is separated by a different delimiter can be given using the
    # sep argument. So rFunctions.readCsvFile('example_files/input/mzML.csv', sep=',') would separate on commas. Additional arguments can
    # be found in the documentation of rFunctions.readCsvFile().
    precursorPerFeatureDataframe = rFunctions.readCsvFile('example_files/input/feature_precursor.csv', head=True, sep='\t')

    # merge the precursorPerFEatureDataframe and the featDataframeUniq. Because both dataframes have a column named 'id' R's merge function will automatically append
    # the '# precursors' column values from precursorPerFeatureDataframe to the right row. That is, where the value in column 'id' is the same for both dataframes. 
    mergedFeatureDataframe = R.r['merge'](featDataframeUniq, precursorPerFeatureDataframe)

    # Take the log10 of all the values in the 'intensity' column and round them to their nearest full number (because discrete values needed for the boxplot)
    mergedFeatureDataframe[rFunctions.index(mergedFeatureDataframe, 'intensity')] = R.r['round'](rFunctions.takeLog(featDataframeUniq[rFunctions.index(featDataframeUniq, 'intensity')], 10))
    
    # Retrieves a vector of all the values in the column '# precursors' of mergedFeatureDataframe
    vector1 = mergedFeatureDataframe[rFunctions.index(mergedFeatureDataframe, 'X..precursors')]
    
    # Retrieves a vector of all the values in the column 'intensity' of mergedFeatureDataframe
    vector2 = mergedFeatureDataframe[rFunctions.index(mergedFeatureDataframe,'intensity')]

    # make an instance of rPlots.Plots()
    plots = rPlots.Plots()
   
    # using plots.boxplotFormulae to plot a boxplot. Because the boxplot is the values in the column '# precursors' per value in the column 'intensity', plots.boxplotFormulae 
    # is used instead of plots.boxplotDataframe. First argument is a the name of the ouput file. Second and third argument are 2 vectors which correspond to the x and  y 
    # explained in rpy2's robjects_formulae documentation.  http://rpy.sourceforge.net/rpy2/doc-2.2/html/robjects_formulae.html. 
    # Title is the title of the graph, xlab is the description that will go under the x-axis, y-lab is the description that will go to the y-axis 
    # The first 3 positional arguments are mandatory, the keyworded arguments are given to the **kwargs of barplot and are optional. For more possible arguments 
    # see the rPlots.Plots.barbplot documentation. 
    plots.boxplotFormulae('example_files/output/msms_per_feature_per_intensity_boxplot.png', vector1, vector2, mergedFeatureDataframe, 
                    title = 'MS/MS per feature per intensity', ylab = '# of MS/MS per feature', xlab = 'Rounded log10 of intensity')

    

if __name__ == '__main__':
    feature_per_intensity_histogram()                   # single histogram example
    msms_per_intensity_histogram()                      # single histogram example
    feature_and_MSMS_per_intensity_histogram()          # two overlapping histograms example
    msms_and_spectrum_per_ioncurrent_histogram()        # two overlapping histograms example
    msms_per_feature_barplot()                          # barplot example
    msms_per_feature_per_intensity_boxplot()            # boxplot example
