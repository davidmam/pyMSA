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
Functions that make use of the rpy2 library to work with matrices, dataframes, csv files etc.

B{Possible additions:}

Function that takes n amount of lists of different lengths and adds them in a dataframe, with all the short lists
being filled up with NA's. Should be easy in combination with L{rFunctions.fillNA}

"""

# author: ndeklein
# date:08/02/2012
# summary: Functions to draw graphs and work with dataframes using R through Rpy2

import rpy2.robjects as R
import os

# get the index of a column in a matrix or dataframe base on a column name
def index(matrix, columnName):
    """
    Get the column index number columnName in matrix.
    
    The index returned is a 'python' index, meaning it starts from 0. R indexing starts at 1, so if you want to use this with an R function
    add 1 to the return value.
    
    @type matrix: rpy2.robjects.vectors.DataFrame
    @param matrix: Matrix or DataFrame with named columns.
    @type columnName: string
    @param columnName: Name of one of the columns in matrix
    @rtype: number
    @return: Index of the given column name in the given matrix
    @raise KeyError: columnName does not exist in matrix
    @raise TypeError: matrix is not of type rpy2.robjects.vectors.DataFrame
    @attention: Returns a 'python' index, starting at 0. R indexes start at 1. 
    
    B{Examples}:
    
    Printing the index of the column 'test1' in exampleFrame:
    
    >>> import rpy2.robjects as R
    >>> dict = {'test1': R.IntVector((12,12,15)), 'test2': R.IntVector((32,4,12)), 'test3': R.IntVector((3,12,26))} 
    >>> exampleFrame = R.DataFrame(dict)     # example dataframe. Important to note: because of dictionaries ordering mechanism, in this example the order of columns is test1, test3, test2. The ordering does not affect index().
    >>> print index(exampleFrame, 'test1')   
    0

    Using the column index to extract the values of column 'test1' from testFrame with python's lists bracket syntax:
    
    >>> import rpy2.robjects as R
    >>> dict = {'test1': R.IntVector((12,12,15)), 'test2': R.IntVector((32,4,12)), 'test3': R.IntVector((3,12,26))}       
    >>> exampleFrame = R.DataFrame(dict)     # example dataframe.   
    >>> print testFrame[index(testFrame, 'test2')]   # get the values of column 'test2'
    [1] 32  4 12

    Using the column index to extract the values of column 'test1' from testFrame with R's .rx() function. Note that +1 is added to the index 
    because R's indexing starts at 1 instead of 0:

    >>> import rpy2.robjects as R
    >>> dict = {'test1': R.IntVector((12,12,15)), 'test2': R.IntVector((32,4,12)), 'test3': R.IntVector((3,12,26))}    
    >>> exampleFrame = R.DataFrame(dict)    # example dataframe
    >>> print testFrame.rx(True, index(testFrame, 'test2')+1)  # note the +1, because testFrame.rx() is an R function, so the indexing starts at 1
    [1] 32  4 12
    
    """
    # list that keeps track of all the column names that were given.
    columnList = []
    if isinstance(matrix, R.vectors.DataFrame):
        # counter that keeps track of the column index
        columnCount = 0     
        # for all the column names
        for name in R.r['names'](matrix):
            columnList.append(name)
            # if the given columnName == the column name in the file
            if columnName == name:
                return columnCount
            columnCount += 1
            
        # because a return stops the loop, the raise is only reached if none of the counts found anything. Error message shows which rows it did find
        raise KeyError,'That column name is not in the DataFrame. The only columns found were: '+str(columnList)
    elif isinstance(matrix, R.vectors.Matrix):
        if  str(matrix.colnames) == 'NULL':
            raise ValueError, 'The matrix given to index() has no column names, can not iterate over them. Matrix.colnames is of type: '+str(type(matrix.colnames))
        # counter that keeps track of the column index
        columnCount = 0
        
        # for all the column names
        for name in matrix.colnames:
            columnList.append(name)
            # if the given columnName == the column name in the file
            if columnName == name:
                return columnCount
            columnCount += 1
        raise KeyError,'That column name is not in the Matrix. The only columns found were: '+str(columnList)
    else:
        raise TypeError, 'matrix given to index() is not of type rpy2.robjects.vectors.DataFrame. Instead, is of type: '+str(type(matrix))




# get all the rows from a matrix or dataframe with a unique value at given column
# return a subset of the matrix with only unique values for the given column
def getRowsWithUniqColumn(matrix, columnName):    
    """
    Get all the rows from matrix with unique value in the column columnName.
    
    @type matrix: rpy2.robjects.vectors.DataFrame
    @param matrix: The matrix that you want a subset of
    @type columnName: string
    @param columnName: The name or index of the column you only want the unique values of
    @rtype: rpy2.robjects.vectors.DataFrame
    @return: A subset of matrix with only unique values in column. 
    @raises TypeError: column is not of type str
       
    B{Example}:
    
    Printing a sub dataframe where the values in column 1 have to be unique:
    
    >>> import rpy2.robjects as R
    >>> dict = {'test1': R.IntVector((12,12,15)), 'test2': R.IntVector((32,4,12)), 'test3': R.IntVector((3,12,26))}       # note that test1 has 12 in row 1 and row 2 
    >>> exampleFrame = R.DataFrame(dict)    
    >>> print getRowsWithUniqColumn(testFrame, 'test1')  # now only two of the three rows remain, because test1 had 12 twice in the row
      test1 test3 test2
    1    12     3    32
    3    15    26    12

    """
    
    # getting the not sign of R
    rnot = R.r['!']
    # getting duplicated
    duplicated = R.r['duplicated']
    
    # creating the subset of the matrix, if type == str use the index function, elif type == int use
    # the int itself, else raise a TypeError
    if type(columnName) != str:
        raise TypeError, 'Column given to getRowsWithUniqColumn has to be of type str, was of type:',type(columnName)

    subsetMatrix = R.r['subset'](matrix,  rnot(duplicated(matrix[index(matrix, columnName)])))
       
    return subsetMatrix

# make a submatrix only containing the two given columns of the matrix
# return the submatrix
def getColumns(matrix, *args):
    """
    Make a subset of a matrix or dataframe containing only the columns with column names given to *args.
    
    @type matrix: rpy2.robjects.vectors.DataFrame
    @param matrix: The matrix that you want the subset of
    @type args: string
    @param args: One or more column names that you want in the subset 
    @rtype: rpy2.robjects.vectors.DataFrame
    @return: Subset of matrix only containing columns given to *args
    @raises InputError: No arguments given to *args
    @raises TypeError: matrix is not of type rpy2.robjects.vectors.Matrix or rpy2.robjects.DataFrame
    @raises TypeError: Names passed to *args are not of type str
    
    B{Example}:
    
    Print a sub dataframe with only 2 of the 3 original columns:
        
    >>> import rpy2.robjects as R
    >>> dict = {'test1': R.IntVector((12,12,15)), 'test2': R.IntVector((32,4,12)), 'test3': R.IntVector((3,12,26))}       # note that test1 has 12 in row 1 and row 2 
    >>> testFrame = R.DataFrame(dict)    
    >>> print getColumns(testFrame, 'test1', 'test3')
      test1 test3
    1    12     3
    2    12    12
    3    15    26
    """
    # check that at least one column name has been given to *args. if not raise inputerror
    if len(args) == 0:
        raise TypeError, 'No column name passed to getColumns'
    
    if not isinstance(matrix, R.vectors.DataFrame) and not isinstance(matrix, R.vectors.Matrix):
         raise TypeError, 'matrix given to getColumns is not of type rpy2.robjects.vectors.Matrix or rpy2.robjects.DataFrame. Instead, it is of type: '+str(type(matrix))


    # the dict that is going to hold the info for the new subframe
    subFrameDict = {}
    # creating a vector from the given column in the given matrix, if type is not string raise a type error
    for colName in args:
        if type(colName) != str:
            raise TypeError, 'Column name given to args: '+str(colName)+' is not of type str. Instead, is of type: '+str(type(colName))
        # have to do index +1 because of python's indexing (see index documentation for more info)
        subFrameDict[colName] = matrix.rx(True, index(matrix, colName)+1)
        
    subFrame = R.DataFrame(subFrameDict)
    return subFrame
    
    
# Take the log of an R type object (like a vector or a matrix, see R documentation about 'log' what types can be used)
def takeLog(x, base):
    """
    Take the logarithm of an R type object.
    The R type is tested on a vector, see R documentation about ?log what other types can be used.
    
    @type x: R variable that works with log() e.g. IntVector. (see R documentation ?log) 
    @param x: Object that you want to take the log of.
    @type base: Number
    @param base: base for the logarithm
    @raises ValueError: base not a positive number
    @rtype: Same as x
    @return: The logarithm of all the values in x. 
    
    B{Example}:
    
    Print the logarithm of a vector:
    
    >>> import rpy2.robjects as R
    >>> vector = R.IntVector((59843, 34982, 12425, 90534, 34532, 54642, 1239, 43534))
    >>> print takeLog(vector, 10)
    [1] 4.777013 4.543845 4.094296 4.956812 4.538222 4.737527 3.093071 4.638829
    """

    if base >= 0:
        log_x = R.r['log'](x, base = base)
    # can't take a negative log, so raise valueerror
    else:
        raise ValueError, 'log has to be a positive number, it was: '+str(base)  
    
    return log_x  

# uses R.r['read.csv']
def readCsvFile(csvFilePath, sep='\t', head=True, na='N/A', **kwargs):
    """
    Read a csv file and return the content.
    Returns a dataframe of the csv file data
    
    @type csvFilePath: string
    @param csvFilePath: The path to the csv file
    @type sep: string
    @param sep: The character to separate the csv file on (default = '\t')
    @type head: bool
    @param head: Boolean if the file to read in has headers or not (default: True)
    @type na: string
    @param na: What do the non available values look like (default = N/A)
    @param kwargs: Any additional options for to R.r['read.csv'] (read R's ?read.csv documentation to see what arguments are possible)
    @rtype: rpy2.robjects.vectors.DataFrame
    @return: Dataframe representation of the csv file
    
    B{Examples}:
    
    reading a csv file separated by tabs, with headers and N/A as not available (the default settings): 
    
    >>> csvDataFrame = readCsvFile('exampleFile.csv')        

    reading a csv file separated by spaces, no headers, not available as NA, and escapes are allowed:
    
    >>> csvDataFrame2 = readCsvFile('exampleFile2.csv', sep=' ', head=False, na='NA', allowEscapes='True')     
    

    """

    if not os.path.exists(csvFilePath):
        raise IOError, 'File or folder cannot be found: '+str(csvFilePath)
    if not type(head) == bool:
        raise TypeError, 'param head given to readCsvFile has to be boolean. Instead is of type: '+str(type(head))
    # this should not ever happen because if csvFilePath was not a string it should have given an IOError
    if not type(csvFilePath) == str:
        raise TypeError, 'param csvFilePath has to be of type str. Instead is of type: '+str(type(csvFilePath))
    csvData = R.r['read.csv'](file=csvFilePath, sep = sep, na=na, **kwargs)
    return csvData


def fillNA(vectorList, amount, rType):
    """
    Fills the given vector with the 'not available' R type (either NA_Logical, NA_Real, NA_Integer, NA_Character or NA_Complex)

    @type vectorList: list
    @param vectorList: List to which 'not available' types will be appended.
    @type amount: number
    @param amount: The amount of 'not availables' to add to vector
    @type rType: The type of 'not available' to use (either NA_Logical, NA_Real, NA_Integer, NA_Character or NA_Complex)
    @rtype: list
    @return: List given to fillNA with added NA's
    @raise TypeError: rType did not contain allowed value
    @raise TypeError: vectorList is not of type list
    @raise TypeError: amount is not of type int
    
    B{Example:}
    
    Add 2 Na_Integers to a list
    
    >>> print rFunctions.fillNA([1,2,3], 2, 'NA_Integer')
    [1,2,3, R.NA_Integer, R.NA_Integer]
    """
    if not isinstance(vectorList, list):
        raise TypeError, 'vectorList given to fillNA is not of type list. Instead, is of type: '+str(type(vectorList))
    if not isinstance(amount, int):
        raise TypeError, 'amount given to fillNA is not of type list. Instead, is of type: '+str(type(amount))
    
    if rType.lower() == 'na_integer':
        NA = R.NA_Integer
    elif rType.lower() == 'na_real':
        NA = R.NA_Real
    elif rType.lower() == 'na_logical':
        NA = R.NA_Logical
    elif rType.lower() == 'na_character':
        NA = R.NA_Character
    elif rType.lower() == 'na_complex':
        NA = R.NA_Complex
    else:
        raise TypeError, 'rType given to fillNA was not allowed. Allowed values are: NA_Logical, NA_Real, NA_Integer, NA_Character or NA_Complex'
   
    # use while amount > 0 so that when comparing list one of length 20 and list2 of length 15 you can do
    # fillNA(list1, list1-list2, 'NA_Integer') and because amount is now negative, it will not add any 
    # NA's to list1
    while amount > 0:
            vectorList.append(NA)    
            amount -= 1
            
    return vectorList
