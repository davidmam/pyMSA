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
Web submitter for MASCOT searches to pipeline MS/MS proteomics experiment
"""

import urllib2
import sys
sys.path.append('/homes/ndeklein/python2.6/site-packages/requests-0.13.1/')
import requests



def test():
    url = "http://mascot.proteomics.dundee.ac.uk/cgi/search_form.pl?FORMVER=2&SEARCH=MIS"
    data = {'SEARCH':'MIS','FORMVER':'1.0.1', 'PEAK':'AUTO','REPTYPE':'peptide', 'ErrTolRepeat':'0','USERNAME':'Niek',
            'USEREMAIL':'me_niek@hotmail.com','COM':'Test','DB':'MaxQuantMouse','CLE':'Trypsin','PFA':'1','QUANTITATION':'None',
            'TAXONOMY':'All entries','TOL':'1.2','TOLU':'Da','PEP_ISOTOPE_ERROR':'0', 'ITOL':'0.6','ITOLU':'Da','CHARGE':'2+',
            'MASS':'Monoisotopic','FORMAT':'Mascot generic','INSTRUMENT':'Default','REPORT':'AUTO'}
    
    files = {'JG-C1-1A.mgf' : open('/homes/ndeklein/Cantrell/JG-C1-1.mgf','rb')}

    r = requests.post(url, data=data, files=files)
    print r.url


    
    #data = urllib.urlencode(values)
    #req = urllib2.Request(url, data)
    #response = urllib2.urlopen(req)
    #the_page = response.read()
    #print the_page



#Server:Apache/2.2.3 (CentOS)
