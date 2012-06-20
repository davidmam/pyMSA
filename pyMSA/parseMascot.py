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
Parser to extract relevant data from a mascot result xml file.
"""

# author: ndeklein
# date:08/02/2012
# summary: Parses a .peaks.mzML file. Makes an iterator object out of the parsing (using yield, not __iter__ and __next__).
from xml.etree import cElementTree
import fileHandling
import collections
import elementFunctions
import re

class Reader():
    """
    
    Generator object to get information from MASCOT result XML files. 
        
    B{Example}:

    Printing all the selements in a file:
    
    >>> mascot = Reader('example_mascot_file.xml')    # make a read instance
    >>> allElements = mascot.getAllElements()    # get all elements of the reader instance, you can now iterate over allElements
    >>> for element in allElements:
    ...    print element
    <Element 'mascot_search_results' at 0x166a05a0>
    <Element 'header' at 0x166a0600>
    <Element 'Date' at 0x6184270>            
    """
    
    
    # initializer, takes a file path as input
    def __init__(self, path, **kwargs):
        self.rt_re= kwargs.get('rt_re',None)
        self.mz_re=kwargs.get('mz_re',None) 
        self.scan_re=kwargs.get('scan_re',None) 
        self.file_re=kwargs.get('file_re',None)
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
        file.isMascot()
        # the current element
        self.element = None
        # current userParam
        # a list of all the keys that can be used for __getItem__
        self.__spectraKeySet = []
        # element dictionary to contain all the elements
        # uses collections.defaultidct to enable unknown keys to be added to the dictionary 
        self.spectraInfo = collections.defaultdict(dict)
        
        self.simpleFlag = True
        
    def setScanRE(self, scan_re):
        '''sets the regular expression used to parse the scan number out from the Mascot file'''
        self.scan_re=scan_re
        
    def setFileRE(self, file_re):
        '''sets the regular expression used to parse the scan number out from the Mascot file'''
        self.file_re=file_re
        
    def setRtRE(self, rt_re):
        '''sets the regular expression used to parse the scan number out from the Mascot file'''
        self.rt_re=rt_re
        
    def setMzRE(self, mz_re):
        '''sets the regular expression used to parse the scan number out from the Mascot file'''
        self.mz_re=mz_re
        
    # Make an iterable function (by using yield) that returns every element in the file
    def getAllElements(self):
        """
        Iterator function that yields all the elements in the file given to Reader()
        
        @rtype: Element
        @return: All the elements in the file
        @raise RuntimeError: No elements in the file

        B{Example}:

        Printing all the selements in a file:
        
        >>> mascot = Reader('example_mascot_file.xml')    # make a read instance
        >>> allElements = mascot.getAllElements()    # get all elements of the reader instance, you can now iterate over allElements
        >>> for element in allElements:
        ...    print element
        <Element 'mascot_search_results' at 0x166a05a0>
        <Element 'header' at 0x166a0600>
        <Element 'Date' at 0x6184270>
        
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
            raise RuntimeError, 'No elements found at getAllElements(), invalid mascot XML file: '+str(self.path)
        
        
    def getAssignedPeptidesMZandRTvalue(self):
        """
        Iterator function that yields all the assigned peptide m/z and retention time value and the accession number of the 
        protein they are assigned to. Does not get any additional information on the peptides
        
        @rtype: dict
        @return: A dict of all the assigned peptides with m/z, RT value and protein description
        
        B{Example:}
        
        Printing all assigned peptide's m/z value, RT value and protein description:
        
        >>> mascot = Reader('example_mascot_file.xml')    # make a read instance
        >>> for result in mascot.getAssignedPeptidesMZandRTvalue():
        ...    print result
        """
        for element in self.getAllElements(): 
            # get the useful info from the element tag
            elementTag = element.tag.split('}')[-1]
            # the protein and peptide information is nested inside hits>hit>protein>pep_scan_title
            if elementTag == 'hits':
                for hit in element:
                    for protein in hit:
                        proteinAccession = elementFunctions.getItems(protein)['accession']
                        for protInfo in protein:
                            protInfoTag = protInfo.tag.split('}')[-1]
                            if protInfoTag == 'prot_desc':
                                prot_desc = protInfo.text
                            elif protInfoTag == 'prot_score':
                                prot_score = protInfo.text
                            elif protInfoTag == 'prot_mass':
                                prot_mass = protInfo.text
                            elif protInfoTag == 'prot_matches':
                                prot_matches = protInfo.text
                            elif protInfoTag == 'prot_matches_sig':
                                prot_matches_sig = protInfo.text
                            elif protInfoTag == 'prot_sequences':
                                prot_sequences = protInfo.text
                            elif protInfoTag == 'prot_sequences_sig':
                                prot_sequences_sig = protInfo.text
                            elif protInfoTag == 'peptide':
                                for pepInfo in protInfo:
                                    pepInfoTag = pepInfo.tag.split('}')[-1]
                                    # cuase this not always exists
                                    pep_num_match = None
                                    if pepInfoTag == 'pep_exp_mz':
                                        pep_exp_mz = pepInfo.text
                                    elif pepInfoTag == 'pep_exp_mr':
                                        pep_exp_mr = pepInfo.text
                                    elif pepInfoTag == 'pep_exp_z':
                                        pep_exp_z = pepInfo.text
                                    elif pepInfoTag == 'pep_calc_mr':
                                        pep_calc_mr = pepInfo.text
                                    elif pepInfoTag == 'pep_delta':
                                        pep_delta = pepInfo.text
                                    elif pepInfoTag == 'pep_miss':
                                        pep_miss = pepInfo.text
                                    elif pepInfoTag == 'pep_score':
                                        pep_score = pepInfo.text
                                    elif pepInfoTag == 'pep_expect':
                                        pep_expect = pepInfo.text
                                    elif pepInfoTag == 'pep_res_before':
                                        pep_res_before = pepInfo.text
                                    elif pepInfoTag == 'pep_seq':
                                        pep_seq = pepInfo.text
                                    elif pepInfoTag == 'pep_res_after':
                                        pep_res_after = pepInfo.text
                                    elif pepInfoTag == 'pep_var_mod':
                                        pep_var_mod = pepInfo.text
                                    elif pepInfoTag == 'pep_var_mod_pos':
                                        pep_var_mod_pos = pepInfo.text
                                    elif pepInfoTag == 'pep_num_match':
                                        pep_num_match = pepInfo.text
                                    elif pepInfoTag == 'pep_scan_title':
                                        pep_scan_title = pepInfo.text
                                        ## TODO allow separate RE to parse mz/rt/scan number  values from the title.
                                        titlepar=self._parseTitle(pep_scan_title)
                                        if titlepar.has_key('mz'):
                                            mz=titlepar['mz']
                                        else:
                                            mz=None
                                        if titlepar.has_key('rt'):
                                            rt=titlepar['rt']
                                        else:
                                            rt=None
                                        if titlepar.has_key('file'):
                                            fileroot=titlepar['file']
                                        else:
                                            fileroot=None
                                        if titlepar.has_key('scan'):
                                            scan=titlepar['scan']
                                        else:
                                            scan=None

#                                        mz = pepInfo.text.split('_')[0]
#                                        rt = pepInfo.text.split('_')[1]
                                        yield {'mz':mz, 'rt':rt, 'protAccession':proteinAccession, 'prot_desc':prot_desc, 
                                               'prot_score':prot_score, 'prot_mass':prot_mass,'prot_matches':prot_matches, 
                                               'prot_matches_sig':prot_matches_sig,'prot_sequences':prot_sequences, 
                                               'prot_sequences_sig':prot_sequences_sig,'pep_exp_mz':pep_exp_mz, 
                                               'pep_exp_mr':pep_exp_mr, 'pep_exp_z':pep_exp_z, 'pep_calc_mr':pep_calc_mr
                                               ,'pep_delta':pep_delta,'pep_miss':pep_miss, 'pep_score':pep_score,
                                               'pep_expect':pep_expect,'pep_res_before':pep_res_before,'pep_seq':pep_seq, 
                                               'pep_res_after':pep_res_after, 'pep_var_mod':pep_var_mod,'pep_var_mod_pos':pep_var_mod_pos
                                               ,'pep_num_match':pep_num_match, 'pep_scan_title':pep_scan_title, 'fileroot':fileroot, 'scannumber':scan}
 
    def _parseTitle(self, title):
        '''uses the object level regular expression definitions to extract the rt, mz, scan and file name parameters from the title string if present'''
        params={}
        if self.rt_re != None:
            try:
                rtm=re.search(self.rt_re, title)
                if rtm:
                    if rtm.group(1):
                        params['rt']=rtm.group(1)
            except:
                pass
        if self.mz_re != None:
            try:
                rtm=re.search(self.mz_re, title)
                if rtm:
                    if rtm.group(1):
                        params['mz']=rtm.group(1)
            except:
                pass
        if self.scan_re != None:
            try:
                rtm=re.search(self.scan_re, title)
                if rtm:
                    if rtm.group(1):
                        params['scan']=rtm.group(1)
            except:
                pass
        if self.file_re != None:
            try:
                rtm=re.search(self.file_re, title)
                if rtm:
                    if rtm.group(1):
                        params['file']=rtm.group(1)
            except:
                pass
        return params



    def getUnassignedPeptidesMZandRTvalue(self):
        """
        Iterator function that yields all the unassigned peptide m/z and retention time value. Does not get any additional information on the peptides
        
        @rtype: dict
        @return: A dict of all the assigned peptides with m/z, RT value and protein description
        
        B{Example:}
        
        Printing all assigned peptide's m/z value, RT value and protein description:
        
        >>> mascot = Reader('example_mascot_file.xml')    # make a read instance
        >>> for result in mascot.getAssignedPeptidesMZandRTvalue():
        ...    print result
        """

        for element in self.getAllElements():
            # get the useful info from the element tag
            elementTag = element.tag.split('}')[-1]
            # the protein and peptide information is nested inside hits>hit>protein>pep_scan_title
            if elementTag == 'unassigned':
                for u_peptide in element:
                    for pepInfo in u_peptide:
                        pepInfoTag = pepInfo.tag.split('}')[-1]
                        pep_num_match = None
                        if pepInfoTag == 'pep_exp_mz':
                            pep_exp_mz = pepInfo.text
                        elif pepInfoTag == 'pep_exp_mr':
                            pep_exp_mr = pepInfo.text
                        elif pepInfoTag == 'pep_exp_z':
                            pep_exp_z = pepInfo.text
                        elif pepInfoTag == 'pep_calc_mr':
                            pep_calc_mr = pepInfo.text
                        elif pepInfoTag == 'pep_delta':
                            pep_delta = pepInfo.text
                        elif pepInfoTag == 'pep_miss':
                            pep_miss = pepInfo.text
                        elif pepInfoTag == 'pep_score':
                            pep_score = pepInfo.text
                        elif pepInfoTag == 'pep_expect':
                            pep_expect = pepInfo.text
                        elif pepInfoTag == 'pep_seq':
                            pep_seq = pepInfo.text
                        elif pepInfoTag == 'pep_var_mod':
                            pep_var_mod = pepInfo.text
                        elif pepInfoTag == 'pep_var_mod_pos':
                            pep_var_mod_pos = pepInfo.text
                        elif pepInfoTag == 'pep_num_match':
                            pep_num_match = pepInfo.text
                        elif pepInfoTag == 'pep_scan_title':
                            pep_scan_title = pepInfo.text
                            #mz = pepInfo.text.split('_')[0]
                            #rt = pepInfo.text.split('_')[1]
                            ## TODO allow separate RE to parse mz/rt/scan number  values from the title. 
                            titlepar=self._parseTitle(pep_scan_title)
                            if titlepar.has_key('mz'):
                                mz=titlepar['mz']
                            else:
                                mz=None
                            if titlepar.has_key('rt'):
                                rt=titlepar['rt']
                            else:
                                rt=None
                            if titlepar.has_key('file'):
                                fileroot=titlepar['file']
                            else:
                                fileroot=None
                            if titlepar.has_key('scan'):
                                scan=titlepar['scan']
                            else:
                                scan=None
                            yield {'mz':mz, 'rt':rt,'pep_exp_mz':pep_exp_mz, 'pep_exp_mr':pep_exp_mr, 
                                   'pep_exp_z':pep_exp_z, 'pep_calc_mr':pep_calc_mr,'pep_delta':pep_delta,
                                   'pep_miss':pep_miss, 'pep_score':pep_score,'pep_expect':pep_expect,
                                   'pep_seq':pep_seq, 'pep_var_mod':pep_var_mod,'pep_var_mod_pos':pep_var_mod_pos, 
                                   'pep_num_match':pep_num_match,'pep_scan_title':pep_scan_title, 'scannumber':scan, 'fileroot':fileroot}
