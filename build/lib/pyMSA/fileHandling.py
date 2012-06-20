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
Handling the opening of files, checking for file vadility and existence. 
"""

# author: ndeklein
# date:08/02/2012
# summary: Writes readerInstance (from parseFeatureXML.Reader) to output files.

import os
import warnings

class FileHandle():
    """
    A handle to easily validate the correctness of a file
        
    >>> fileHandle = FileHandle('exampleFeatureXMLfile.featureXML')
    >>> fileHandle.isXML()
    >>> fileHandle.isFeatureXML()
    """
    def __init__(self,path):
        """
        @type path: string
        @param path: Path of a file
        """
        #test if the file is there to get an early error if it's not
        test = open(path)
        test.close()
        self.path = path
        
    # Check if the file provided is a xml file
    def isXML(self):
        """
        Check if <?xml is in the first line of the file.
        
        @raise IOError: File given to FileHandle is not a valid XML file. 

        B{Example}:

        Check if a file is valid XML

        >>> fileHandle = FileHandle('example_featureXML_file.featureXML')
        >>> fileHandle.isXML() # returns None if it is valid, raises error if it is invalid
        
        """
        inFile = open(self.path)
        # if the first line of the file doesn't start with <?xml: close the file and raise IOError: 'Not a valid xml file'
        if not inFile.readline().startswith('<?xml'):
            inFile.close()
            raise IOError, self.path+' is not a valid xml file'
        else:
            inFile.close()
            return
            
    # Check if the file provided is a featureXML file
    def isFeatureXML(self):
        """
        Check if <featureMap is in the second line of the file.

        @raise IOError: File given to FileHandle is not a valid .featXML file. 
        @raise Warning: File given to FileHandle does not have 'software' in the 4th line
        @raise Warning: Version of software is not of 1.9.0 or higher
        
        B{Example}:
        
        Checking if a featureXML file is valid
    
        >>> fileHandle = FileHandle('example_featureXML_file.featureXML')
        >>> fileHandle.isFeatureXML() # returns None if it is valid, raises error if it is invalid
        
        """
        inFile = open(self.path)
        # read the first line
        inFile.readline()
        # if the second line of the file doesn't start with <featureMap: Return 'Not a featureXML file'
        if not inFile.readline().startswith('<featureMap'):
            inFile.close()
            raise IOError, self.path+' is not a valid featureXML file'
        else:
            # read max of 10 lines (because the software line can be in different place with different version of featureXML
            for i in range(0,9): # loop 10 times
                # read each line
                softwareLine = inFile.readline()
                # if software == in softwareLine, break
                if 'software' in softwareLine:
                    break
                
            # if 'software' is not in softwareLine this means that the first 10 lines did not contain software
            if not 'software' in softwareLine:
                # give a warning because it is not vital for the functioning of the program
                warnings.warn('software information of the featureXML file: \''+str(self.path)+'\' not in the first 10 lines, software version used unknown')
                inFile.close
            else:
                version = softwareLine.split('version="')[1].split('"')[0]
                # if the version is not 1.7.0 - 1.9.0
                if not int(version.replace('.','')) >= 190:
                    warnings.warn('pyMS is only tested on version 1.9.0 of FeatureFinder. Older versions might not work. Found version: '+str(version)+' for your file:' +str(self.path)+'')
            inFile.close()
    
    # check if the file provided is a mzml or peaks.mzml file
    def isMzML(self):
        """
        Check if <mzML is in the second or third line of the file.

        @raise IOError: File given to FileHandle is not a valid .mzML or .peaks.mzML file. 

        B{Example}:
    
        Checking if an mzml file is valid
    
        >>> fileHandle = FileHandle('exampleMzMLfile.mzML')
        >>> fileHandle.isXML() # returns None if it is valid, raises error if it is invalid
        
        Checking if a peaks.mzml file is valid
        
        >>> fileHandle = FileHandle('example_peaks_mzML_file.peaks.mzML')
        >>> fileHandle.isMzML()
        """
        
        inFile = open(self.path)
        # read the first line
        inFile.readline()
        # if the second line and the third line don't start with mzML: Return: 'Not a .mzML or .peaks.mzML file'
        # the second .readline() after the and not reads the second line (because .readline() pops the line out of buffer)
        if not 'mzML' in inFile.readline() and not 'mzML' in inFile.readline():
            inFile.close()
            raise IOError, self.path+' is not a valid .mzML or .peaks.mzML file'
        else:
            inFile.close()

    def isMascot(self):
        """
        Check if <mascot_search_results is in the second line of the file.

        @raise IOError: File given to FileHandle is not a valid mascot result XML file. 

        B{Example}:
    
        Checking if an mascot file is valid
    
        >>> fileHandle = FileHandle('exampleMascotFile.xml')
        >>> fileHandle.isMascot() # returns None if it is valid, raises error if it is invalid
        """
        
        inFile = open(self.path)
        # read the first line
        inFile.readline()
        # if the second line and the third line don't start with mzML: Return: 'Not a .mzML or .peaks.mzML file'
        # the second .readline() after the and not reads the second line (because .readline() pops the line out of buffer)
        if not 'mascot_search_results' in inFile.readline():
            inFile.close()
            raise IOError, self.path+' is not a valid mascot result xml file'
        else:
            inFile.close()
    
    
    # return the absolute path of the file
    def getFile(self):
        """
        Get the absolute path of the file given to FileHandle
        
        @rtype: string
        @return: The absolute path of the file given to FileHandle
        
        B{Example}:
        
        Print the full path of a file given to FileHandle:
        
        >>> fileHandle = FileHandle('example_featureXML_file.featureXML')
        >>> print 'The full path is:',fileHandle.getFile()
        The full path is: example_featureXML_file.featureXML
        """
        return os.path.abspath(self.path)
