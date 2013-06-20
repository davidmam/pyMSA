# Copyright (c) 2012 - D.M.A.Martin
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

'''
Helper wrappers for DB loading and analysis.
'''

from pyMSA import database, parseFeatureXML, parseMascot,parseConsensusXML
import pymzml
from Unimod.unimod import database as unimod
from base64 import b64decode
from struct import unpack
import numpy
import MSPlot.msplot3d


class HelperMySQL():
    """
    Wraps the pyMSA database interaction to avoid repetitive use of code.
    B{Example:}
    db=HelperMySQL("dbhost","dbuser", password,"mydb", "RUN_4", scan_re=r'.*scans:(\d+).*')
    db.loadMzML(mzmlfile)
    db.loadFeatureXML(featureXMLfile, intensity_cutoff)
    db.loadMascotXML(mascotXMLfile)
    db.loadConsensusXML(ConsensusXMLfile, tag)
    db.getStatistics()
    
    """

    def __init__( self, host, user, password, database, runtag=None, scan_re=None, rt_re=None, mz_re=None, file_re=None):
        """
        @type host: string
        @param host: the host, where the MySQL database is located
        @type user: string
        @param user: database user name
        @type password: string
        @param password: the user's account password
        @type database: string
        @param database: the database name
        @type runtag: string
        @param runtag: the MS run identifier tag
        @type mz_re: string
        @param mz_re: Regular expression for parsing the from Mascot title strings.
        @type rt_re: string
        @param rt_re: Regular expression for parsing the from Mascot title strings.
        @type scan_re: string
        @param scan_re: Regular expression for parsing the from Mascot title strings.
        @type file_re: string
        @param file_re: Regular expression for parsing the from Mascot title strings.
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.runtag = runtag
        self.rt_re = rt_re
        self.mz_re = mz_re
        self.scan_re = scan_re
        self.file_re = file_re
        self.runid=0
        self.placeholder='%s'
        self.connectionType = 'mysql'
        self.dbsearchgroups={}
        if runtag !=None:
            self._setRunTag()
        self._getSearchGroups()

    def addrun(self, runtag, mzmlfile, description=None):
        ''' db.addrun(runtag, mzmlfile[, description])'''
        self.runtag=runtag
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            self.placeholder=fillDatabase.placeholder
            cursor=fillDatabase.connect.cursor
            cursor.execute("SELECT msrun_id FROM `msrun` WHERE msrun_name = "+self.placeholder+"",  (str(self.runtag),))
            msrun_id = cursor.fetchone()
            if msrun_id ==None:
                fillDatabase.fillMsrun(mzmlfile)
                if description !=None:
                    fillDatabase.updateDescription(description)
                self._setRunTag()
            else:
                raise Exception("Run with tag %s already in database"%runtag)

    def _setRunTag(self):
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            self.placeholder=fillDatabase.placeholder
            cursor=fillDatabase.connect.cursor
            cursor.execute("SELECT msrun_id FROM `msrun` WHERE msrun_name = "+self.placeholder+"",  (str(self.runtag),))
            msrun_id = cursor.fetchone()
            if msrun_id ==None:
                raise Exception("Name %s not found in database"%self.runtag)
            self.runid=msrun_id[0]

    def switchrun(self, runtag=None):
        '''switchrun(runtag=None)
        Switch to the named run or return the current run name if runtag == None'''
        if runtag !=None:
            self.runtag=runtag
            self._setRunTag()
        return runtag

    def loadmzML(self, mzmlfile):
        '''loadmzML( mzmlfile)
        loads the MS2 spectra in mzmlfile to the msrun specified as runtag''' 
        if self.runtag==None:
            raise Exception('No run specified to append spectra to')

        if mzmlfile==None:
            raise Exception("No mzML file specified")

        mzmlInstance=pymzml.run.Reader(mzmlfile)

        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            
            fillDatabase.fillSpectrum(mzmlInstance)

    def linkFeatures(self):
        '''linkFeatures()
        loads the features defined in featureXMLfile to the msrun specified as runtag, 
        optionally linking spectra to features (default true)''' 
        if self.runtag==None:
            raise Exception('No run specified to append spectra to')
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            fillDatabase.linkSpectrumToFeatureNew()
            


    def loadFeatureXML(self, featureXMLfile, cutoff=0, link=True):
        '''loadFeatureXML( featureXMLfile, cutoff=0, link=True)
        loads the features defined in featureXMLfile to the msrun specified as runtag, 
        optionally linking spectra to features (default true)''' 
        if self.runtag==None:
            raise Exception('No run specified to append spectra to')

        if featureXMLfile==None:
            raise Exception("No mzML file specified")
        if cutoff==0:
            raise Exception("an intensity cutoff must be specified")
        reader=parseFeatureXML.Reader(featureXMLfile)
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            
            fillDatabase.fillFeatures(reader, intensity_cutoff=float(cutoff))
            if link==True:
                fillDatabase.linkSpectrumToFeature()

    def loadConsensusXML(self, consensusXMLfile, tag='Auto'):
        '''loadConsensusXML( consensusXMLfile, tag='Auto')
        loads the consensus features defined in consensusXMLfile 
        with the experiment name specified as tag''' 
        if self.runtag==None:
            raise Exception('No run specified to append spectra to')

        if consensusXMLfile==None:
            raise Exception("No consensusXML file specified")
        reader=parseConsensusXML.Reader(consensusXMLfile)
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            
            fillDatabase.fillConsensus(reader, tag )

    def setScan_re(self,scan_re):
        ''' setScan_re(scan_re)
        get/set scan_re'''
        if scan_re !=None:
            self.scan_re=scan_re
        return self.scan_re

    def setRt_re(self,rt_re):
        ''' setRt_re(rt_re)
        get/set rt_re'''
        if rt_re !=None:
            self.rt_re=rt_re
        return self.rt_re

    def setMz_re(self,mz_re):
        ''' get/set mz_re'''
        if mz_re !=None:
            self.mz_re=mz_re
        return self.mz_re

    def setFile_re(self,file_re):
        ''' get/set file_re'''
        if file_re !=None:
            self.file_re=file_re
        return self.file_re

    def loadMascotXML(self, mascotXMLfile, dbsearchgroup=0):
        '''loadMascotXML(mascotXMLfile, dbsearchgroup=0)
        Load the results of the Mascot search in mascotXMLfile and append them to the MS run.
        The regular expressions for scan number, or rt and mz must be set or the method 
        will fail silently.
        dbsearchgroup is the parameter group used for the search to allow grouping of different search 
        strategies on the same input spectra.
        '''
        if self.runtag==None:
            raise Exception('No run specified to append results to')

        if mascotXMLfile==None:
            raise Exception("No mascot XML file specified")

        mascot=parseMascot.Reader(mascotXMLfile, scan_re=self.scan_re, rt_re=self.rt_re, mz_re=self.mz_re, file_re=self.file_re)
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            searchid=fillDatabase.fillDBSearch(mascotXMLfile, dbsearchgroup)
            fillDatabase.fillMascot(mascot, dbsearch=searchid)

    def _getSearchGroups(self):
        '''retrieves db search group details from the database for local storage as self.searchgroups'''
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            for x in fillDatabase.dbsearchgroups.keys():
                self.dbsearchgroups[x]=fillDatabase.dbsearchgroups[x]
        

    def addSearchGroup(self,tag, description, engine):
        '''addSearchGroup(tag, description, engine)
        Add a MS search group. This is essentially a protocol for the 
        database search and allwos grouping of different search protocols.
        '''
        if self.dbsearchgroups.has_key(tag):
            return self.dbsearchgroups[tag]
        else:
            if tag != None and description !=None and engine !=None:
                with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
                    fillDatabase = database.FillDatabase(sqlCon, self.runtag)
                    grpid=fillDatabase.fillDBSearchGroup(tag,description, engine)
                    self.dbsearchgroups[tag]=grpid
                    return grpid

    def mapFeatures(self, fXML_1, fXML_2, trafoXML):
        ''' mapFeatures(fXML_1, fXML_2, trafoXML)
        Maps features between two featureXML files fXML_1 and fXML_2 with the linear trafoXML file generated by
        e.g. MapAlignerPoseClustering
        '''
        if self.runtag==None:
            raise Exception('No run specified to append results to')

        if fXML_1==None or fXML_2==None or trafoXML==None :
            raise Exception("Not all XML files specified")
        reader1=parseFeatureXML.Reader(fXML_1)
        reader2=parseFeatureXML.Reader(fXML_2)
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            
            fillDatabase.fillFeatureMapping(reader1, reader2, trafoXML)


    def runStatistics(self):
        '''runStatistics()
        Performs some simple statistical counting and reporting on the MS run'''
        results={}
        queries={"1. features by intensity and charge": "select intensity_cutoff,charge, count(feature_id) as Features from feature where msrun_msrun_id=%s group by intensity_cutoff,charge order by intensity_cutoff, charge"%self.placeholder,
                 "2. ms2 spectra": "select count(spectrum_id) as Spectra from spectrum where ms_level=2 and msrun_msrun_id=%s"%self.placeholder,
                 "3. features with spectra" : "select count(distinct feature_id) as Features from feature f inner join feature_has_MSMS_precursor m on m.feature_feature_table_id=f.feature_table_id where f.msrun_msrun_id=%s"%self.placeholder,
                 "4. spectra in features": "select count(distinct MSMS_precursor_precursor_id) as Spectra from feature f inner join feature_has_MSMS_precursor m on m.feature_feature_table_id=f.feature_table_id where f.msrun_msrun_id=%s"%self.placeholder,
                 "5. features with Mascot results" : "select count(distinct feature_id) as 'Features with peptide'  from feature f inner join feature_has_MSMS_precursor m on m.feature_feature_table_id=f.feature_table_id inner join MSMS_precursor p on p.precursor_id=m.MSMS_precursor_precursor_id inner join MASCOT_peptide mp on mp.precursor_precursor_id=p.precursor_id where f.msrun_msrun_id=%s"%self.placeholder,
                 "6. features with good Mascot results (>25)" : "select count(distinct feature_id) as 'Features with peptide'  from feature f inner join feature_has_MSMS_precursor m on m.feature_feature_table_id=f.feature_table_id inner join MSMS_precursor p on p.precursor_id=m.MSMS_precursor_precursor_id inner join MASCOT_peptide mp on mp.precursor_precursor_id=p.precursor_id where mp.pep_score >25 and f.msrun_msrun_id=%s"%self.placeholder,
                 "7. Single Scan Features": "select count(*) from (select min(mz) as mz, feature_table_id, min(rt) as minrt, max(rt) as maxrt from  feature f inner join convexhull c on c.feature_feature_table_id = f.feature_table_id where msrun_msrun_id=%s group by feature_table_id ) a where maxrt >minrt"%self.placeholder
                 
}
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            cursor=fillDatabase.connect.cursor
            for q in queries.keys():
                cursor.execute(queries[q], (self.runid,))
                results[q]=cursor.fetchall()

        report="%s\n=========================\n"%self.runtag
        
        for r in sorted(results.keys()):
            report=report + "%s\n==========================\n"%r
            for f in results[r]:
                report=report+"%s\n"%'\t'.join([str(x) for x in f])
            report=report+'\n'
        return report
    # count number of features with each intensity cutoff.
    # count number of spectra
    # features with spectra
    # spectra in/outside features
    # spectra with mascot result (any, >25) inside/outside features
    # features with mascot result (any, >25)

    def groupFeaturesByCharge(self, charges=[2,3,4], tolerance=0.01, cutoff=None, ppm=False, tag="auto"):
        '''groupFeaturesByCharge(charges=[2,3,4], tolerance=0.01, cutoff=None, ppm=False, tag="auto")
        Create feature groups where features correspond to different charge states of coeluting features
        '''
        chargelinks={}
        charges.sort()
        if cutoff==None:
            raise Exception('A valid intensity cutoff must be selected')
        else:
            cutoff=float(cutoff)
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            cursor=fillDatabase.connect.cursor
            cursor.execute('BEGIN')
            cursor.execute('set @hmass := %s'%self.placeholder, (float(unimod.get_element('H')['mono_mass']),))
            cursor.execute("select feature_group_name, feature_group_id from feature_group_type")
            for g in cursor.fetchall():
                chargelinks[g[0]]=g[1]
            for p in range(len(charges)):
                for q in range(p+1, len(charges)):
                    grouptag="Charge Pair - %s+/%s+"%(charges[p], charges[q])
                    groupid=None
                    try:
                        groupid=chargelinks[grouptag]
                    except:
                        cursor.execute("INSERT INTO `feature_group_type` ( feature_group_name, feature_group_description, iso_rt, fixed_delta) values (%s,%s,%s,%s)"%(self.placeholder,self.placeholder,self.placeholder,self.placeholder), ( grouptag, "Co-eluting paired charge states %s+ and %s+"%(charges[p], charges[q]), True, 0.0))
                        cursor.execute("SELECT LAST_INSERT_ID()")
                        groupid=cursor.fetchone()[0]
                    sql="insert into feature_pair (feature_group_id, feature_high_id, feature_low_id, experiment) select "+str(groupid)+", a.feature_table_id, b.feature_table_id, '"+tag+"' from "+\
'(select f.feature_table_id,(mzmin-@hmass)*charge as parentmass, rtmin, rtmax  from feature f inner join convexhull_edges c on c.feature_feature_table_id=f.feature_table_id where f.msrun_msrun_id=%s and f.charge=%s and f.intensity_cutoff=%s ) a ' +\
' inner join '+\
'(select f.feature_table_id,(mzmin-@hmass)*charge as parentmass, rtmin, rtmax  from feature f inner join convexhull_edges c on c.feature_feature_table_id=f.feature_table_id where f.msrun_msrun_id=%s and f.charge=%s and f.intensity_cutoff=%s ) b '+\
'on a.parentmass between b.parentmass-%s and  b.parentmass+%s  and (a.rtmin+a.rtmax)/2 between b.rtmin and b.rtmax'
                    sql=sql%(self.placeholder,self.placeholder,self.placeholder,self.placeholder,self.placeholder,self.placeholder,self.placeholder,self.placeholder)

                    cursor.execute(sql,(self.runid, charges[p],cutoff, self.runid, charges[q],cutoff, tolerance, tolerance))
            cursor.execute('COMMIT')


    def groupFeaturesByLabel(self, label, delta, tolerance=0.001, ppm=False, tag='auto', cutoff=10000):
        '''groupFeaturesByLabel(label, delta, tolerance=0.001, ppm=False, tag='auto', cutoff=10000)
        Create Feature Group entries where co-eluting features are separated by delta/charge +/- tolerance. These are intended to be SILAC labels.
        db.groupFeaturesByLabel(self, label, delta, tolerance=0.001, ppm=False, tag='auto', cutoff=10000)
        label is a name for the label, 
        delta is the mass difference, 
        tolerance is tolerance in Da, 
        ppm is currently unused
        tag is a user defined tag to group labels, cutoff is the feature 'intensity_cutoff' value to limit the search to one set of features.

        '''
        chargelinks={}
        if cutoff==None:
            raise Exception('A valid intensity cutoff must be selected')
        else:
            cutoff=float(cutoff)
        delta=float(delta)
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            cursor=fillDatabase.connect.cursor
            cursor.execute('BEGIN')
            cursor.execute('set @hmass := %s'%self.placeholder, (float(unimod.get_element('H')['mono_mass']),))
            cursor.execute("select feature_group_name, feature_group_id from feature_group_type")
            for g in cursor.fetchall():
                chargelinks[g[0]]=g[1]
            grouptag="Mass Label: %s"%label
            groupid=None
            try:
                groupid=chargelinks[grouptag]
            except:
                cursor.execute("INSERT INTO `feature_group_type` (feature_group_id, feature_group_name, feature_group_description, iso_rt, fixed_delta) values (%s,%s,%s,%s,%s)"%(self.placeholder,self.placeholder,self.placeholder,self.placeholder,self.placeholder), (len(chargelinks.keys())+1, grouptag, "Co-eluting paired mass labels: %s"%label, True, delta))
                groupid=len(chargelinks.keys())+1
            sql="insert into feature_pair (feature_group_id, feature_high_id, feature_low_id, experiment) select "+str(groupid)+", a.feature_table_id, b.feature_table_id, '"+tag+"' from "+\
'(select f.feature_table_id,(mzmin-@hmass)*charge as parentmass, rtmin, rtmax, charge  from feature f inner join convexhull_edges c on c.feature_feature_table_id=f.feature_table_id where f.msrun_msrun_id=%s and f.intensity_cutoff=%s ) a ' +\
' inner join '+\
'(select f.feature_table_id,(mzmin-@hmass)*charge as parentmass, rtmin, rtmax, charge  from feature f inner join convexhull_edges c on c.feature_feature_table_id=f.feature_table_id where f.msrun_msrun_id=%s and f.intensity_cutoff=%s) b '+\
'on a.parentmass-%s between b.parentmass-%s and  b.parentmass+%s  and a.charge=b.charge and (a.rtmin+a.rtmax)/2 between b.rtmin and b.rtmax'#%(self.placeholder,self.placeholder,self.placeholder,self.placeholder,self.placeholder)

            cursor.execute(sql,(self.runid,cutoff, self.runid,cutoff,delta, tolerance, tolerance))
            cursor.execute('COMMIT')


    def groupFeaturesByDelta(self, label, delta, tolerance=0.005, ppm=False, forward=True, reverse=True, tag='auto'):
        '''groupFeaturesByDelta(label, delta, tolerance=0.005, ppm=False, forward=True, reverse=True, tag='auto')
        Search for features with a delta of exactly delta/charge which may elute before 
        (if forward is True), after (if reverse is True) or at the same time 
        (coelute only if forward and reverse are both False)
        '''

    def matchPeptides(self, peptidedb, tolerance=0.005, ppm=False, fixedmods={},  varmods=[], maxvarmod=1, requiremods=False, modcount=None):
        '''matchPeptides( peptidedb, tolerance=0.005, ppm=False, fixedmods={},  varmods=[], maxvarmod=1, requiremods=False, modcount=None)
matches features to the peptides in the database. Include Mascot assignments if present.
        fixedmods={'C':deltamass,...}
        varmods=[(deltamass, ('R','K')),...]
        '''
        
        modlist=[]
        modcountlist=[]
        for k in fixedmods.keys():
            modlist.append("((length(fragment_sequence)-length(replace(fragment_sequence, '%s', '')))*%s)"%(k, fixedmods[k]))
        withmods=''
        if requiremods and len(varmods)>0:
            withmods=' and varmods >0'
            if modcount !=None:
                withmods=' and varmods =%s'%modcount
        for v in varmods:
            rescounts=[]
            for r in v[1]:
                rescounts.append("(length(fragment_sequence)-length(replace(fragment_sequence, '%s', '')))"%r)
            modcountlist.append("least(%s,%s)"%("+".join(rescounts),maxvarmod))
            modlist.append("(least(%s,%s)*%s)"%("+".join(rescounts),maxvarmod,v[0]))    
        if len(modlist)>0:
            mods="+%s"%"+".join(modlist)
        else:
            mods=""
        if len(modcountlist) >0:
            modcounts="+".join(modcountlist)
        else:
            modcounts='0'
        sql="select distinct feature_table_id, round(mz, 5)as `observed mz`, charge, round(mz-(@hmass+(("+\
            "fragment_mono_mass)/charge)), 5) as `delta mz`,round(abs(1000000*(mz-(@hmass+(("+\
            "fragment_mono_mass)/charge)))/mz),1) as `delta mz ppm`, minrt, maxrt, protein_accession,"+\
            "fragment_start, fragment_end, round(fragment_mono_mass, 5) as `parent mass`, "+\
            "fragment_sequence, varmods, intensity, ifnull(foo, 'No MS2') as `MS2 precursor`, pep_seq, pep_delta, "+\
            "pep_score, pep_var_mod, pep_var_mod_pos from (select min(mz) as mz, feature_table_id, charge, intensity, min(rt) as minrt, "+\
            "max(rt) as maxrt from  feature f inner join convexhull c on c.feature_feature_table_id = "+\
            "f.feature_table_id where msrun_msrun_id=%s group by feature_table_id, charge, intensity ) a  "+\
            "inner join (select protein_accession, fragment_start, fragment_end, fragment_sequence, fragment_mono_mass"+mods+" as fragment_mono_mass,"+modcounts+" as varmods  from peptide_fragment where fragment_database_id=%s ) p on (a.mz-@hmass)* charge between p.fragment_mono_mass"+\
            "-0.01 and p.fragment_mono_mass+0.01 left outer join (select distinct "+\
            "feature_feature_table_id as foo, pep_seq, pep_score,pep_delta, pep_var_mod, pep_var_mod_pos from feature_has_MSMS_precursor "+\
            "f inner join MSMS_precursor m on m.precursor_id=f.MSMS_precursor_precursor_id left outer join "+\
            "MASCOT_peptide p on p.precursor_precursor_id=m.precursor_id ) h on h.foo=a.feature_table_id "+\
            "where maxrt >minrt"+withmods
        matches={}
        fields=("feature_table_id","observed mz", "charge","delta mz","delta mz ppm", "minrt", "maxrt", 
                "protein_accession","fragment_start", "fragment_end","parent mass", "fragment_sequence", "variable modifications",
                "intensity","MS2 precursor", "pep_seq", "pep_delta","pep_score", "pep_var_mod", "pep_var_mod_pos")
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            cursor=fillDatabase.connect.cursor
            cursor.execute("set @hmass:=%s",unimod.get_element('H')['mono_mass'])
            cursor.execute(sql, (self.runid, peptidedb))
            for p in cursor.fetchall():
                featureMatch={"feature_table_id":p[0]}
                for f in range(len(fields)):
                    featureMatch[fields[f]]=p[f]
                try:
                    matches[p[0]].append(featureMatch)
                except:
                    matches[p[0]]=[featureMatch,]
        return matches
                
                

    def peptideReport(self, peptidedb, fixedmods={}, varmods=[], tolerance=0.005, maxmods=2, outfile="peptides.txt"):
        '''peptideReport(peptidedb, fixedmods={}, varmods=[], tolerance=0.005, maxmods=2, outfile="peptides.txt")
        run a series of queries, putting the results into a text file that can then be opened in Excel.
        fixedmods apply to all {'C': 57.00,} etc.
        varmods are run in permutations (and no mods as a baseline.) ((delta,[residues]), (delta, (residues)),..) 
        All hits are aggregated by feature then output in spreadsheet format to outfile (default peptides.txt
        '''
        
        # collect baseline
        features=self.matchPeptides(peptidedb, fixedmods=fixedmods, tolerance=tolerance)
        for p in range(1,2**(len(varmods)-1)):
            vml=[]
            for v in range(len(varmods)):
                if ((2**v) & p) >0:
                    vml.append(varmods[v])
            for mm in range(1,maxmods):
                modfeat=self.matchPeptides(peptidedb, fixedmods=fixedmods, varmods=vml, maxvarmod=maxmods, tolerance=tolerance, requiremods=True, modcount=mm)
                for p in modfeat.keys():
                    try:
                        features[p].extend(modfeat[p])
                    except:
                        features[p]=modfeat[p]
        
        fh=open(outfile, "w")
        fh.write("\t".join([str(x) for x in sorted(features[features.keys()[0]][0].keys())])+"\n")
        for k in sorted(features.keys()):
            for m in features[k]:
                fh.write("\t".join([str(m[f]) for f in sorted(m.keys())])+"\n")
        fh.close()

    def _duplicatedPeptides(pm1, pm2):
        '''test to see whether two peptide matches are duplicates'''
        if len(pm1.keys()) != len(pm2.keys()):
            return False
        for k in pm1.keys():
            try:
                if pm1[k] != pm2[k]:
                    return False
            except:
                return False
        return True

    def findSILACprotein(self, proteinid, peptidedb, msrunlist, fixedmods={},labels={'R': 'Label:13C(6)', 'K': 'Label:2H(4)'}):
        '''findSILACprotein( proteinid, peptidedb, msrunlist, fixedmods={},labels={'R': 'Label:13C(6)', 'K': 'Label:2H(4)'})
        Extracts putative SILAC pairs from the runs in runlist
        db.findSILACprotein('proteinid', peptidefragmentdbid, runs, fixedmods, labels)
'''
        modlist=[]
        for m in fixedmods.keys():
            modlist.append("((length(fragment_sequence)-length(replace(fragment_sequence, '%s','')))*%s)"%(m, fixedmods[m]))
        if len(modlist) > 0:
            mods="+%s"%"+".join(modlist)
        else:
            mods=""

        try:
            runs=",".join([str(x) for x in msrunlist])
        except:
            runs=msrunlist

        sql="select distinct a.msrun_msrun_id as run_id, a.feature_table_id as light_id, protein_accession,fragment_start as start, fragment_sequence as peptide, fragment_end as end, a.mz as light_mz, a.charge, a.minrt as `RT start L`, a.maxrt as `RT end L`, parentmass, deltamass, a.intensity as `light intensity`,b.feature_table_id as heavy_id,  b.mz as heavy_mz, b.charge as `charge H`, b.minrt as `RT start H`, b.maxrt as `RT end H`, b.intensity as `intensity H`, a.intensity/b.intensity as ratio from (select msrun_msrun_id, feature_table_id, protein_accession, fragment_start, fragment_sequence, fragment_end, mz, charge, minrt, maxrt,parentmass, parentmass-((mz-@hmass)*charge) as deltamass, intensity from (select min(mz) as mz, charge, min(rt) as minrt, max(rt) as maxrt, feature_table_id, msrun_msrun_id, intensity from feature f inner join convexhull c on c.feature_feature_table_id=f.feature_table_id where msrun_msrun_id in (%s) group by feature_table_id, charge, intensity ) a inner join ( select fragment_mono_mass, fragment_mono_mass%s as parentmass, fragment_start, fragment_sequence, fragment_end, protein_accession from peptide_fragment where protein_accession='%s' and fragment_database_id=%s) as f on (mz-@hmass)*charge between parentmass-0.01 and parentmass+0.01)a inner join (select min(mz) as mz, charge, min(rt) as minrt, max(rt) as maxrt, feature_table_id, msrun_msrun_id, intensity from feature f inner join convexhull c on c.feature_feature_table_id=f.feature_table_id where msrun_msrun_id in (%s) group by msrun_msrun_id,feature_table_id, charge, intensity )b on b.mz-(a.mz+(%%s/a.charge)) between -0.005 and 0.005 and a.maxrt >b.minrt and b.maxrt > a.minrt  and a.charge=b.charge and a.msrun_msrun_id=b.msrun_msrun_id where right(fragment_sequence,1) = '%%s'"%(runs, mods, proteinid,peptidedb, runs)
        labelsql="set @silac%s:=%s"
        hits=[["run_id", "light_id", "protein_accession","start","peptide", "end","light_mz","charge", "RT start L", "RT end L", "parentmass", "deltamass","intensity L","heavy_id","heavy_mz","charge H","RT start H","RT end H","intensity H","ratio"],]
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            cursor=fillDatabase.connect.cursor
            cursor.execute("BEGIN")
            cursor.execute("set @hmass:=%s"%unimod.get_element('H')['mono_mass'])
            for l in labels.keys():
                try:
                    silacmass=unimod.get_label(labels[l])['delta_mono_mass']
                    #print labelsql%(l,silacmass)
                    cursor.execute(labelsql%(l,silacmass))
                    #print sql%(l,l)
                    cursor.execute(sql%(silacmass,l))
                    for p in cursor.fetchall():
                        hits.append(p)
                except Exception, e:
                    print "An Error occured: %s"%e
            cursor.execute("COMMIT")

        return hits

    def getMS1Scan(self, rt=None, scan=None, rtrel="more", runid=None):
        '''retrieve a scan with ms_level 1 by scan number or by RT.
        '''
        if runid==None:
            runid=self.runid
        if rt==None and scan==None:
            raise Exception("Specify RT or Scan to retrieve MS1 spectrum")
        
        if  scan==None:
            scanrel='>'
            scanorder='asc'
            if rtrel=='less':
                scanrel='<='
                scanorder='desc'
            # get scan as lowest ms1 scan with rt > rt
            sql="select spectrum_index from spectrum where scan_start_time "+scanrel+" %s and ms_level=1 and msrun_msrun_id=%s order by scan_start_time "+scanorder+" limit 1"
            with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
                fillDatabase = database.FillDatabase(sqlCon, self.runtag)
                cursor=fillDatabase.connect.cursor
                cursor.execute(sql,(rt, runid))
                try:
                    result=cursor.fetchone()
                    scan=result[0]
                except:
                    raise Exception("Error retrieving scan for RT %s in run %s: %s"%(rt, self.runid, sql%(rt, self.runid)))
        
        return self._getscan(scan)
        
    def _getscan(self, scanindex, runid=None):
        '''retrieves a decoded scan entry. If it is MS2 it includes parent ion and charge state'''
        if runid==None:
            runid=self.runid
        sql="SELECT spectrum_index,scan_start_time, binary_data_mz, binary_data_rt, ms_level, ion_mz, charge_state from spectrum s left outer join MSMS_precursor p on s.spectrum_id=p.spectrum_spectrum_id where msrun_msrun_id=%s and spectrum_index=%s"
        result=None
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            cursor=fillDatabase.connect.cursor
            cursor.execute(sql,(runid, scanindex))
            result=cursor.fetchone()
            if result !=None:
                mzdata=b64decode(result[2].encode('utf-8'))
                idata=b64decode(result[3].encode('utf-8'))
                mzarr=unpack('<%sd'%(len(mzdata)/8),mzdata) 
                iarr=unpack('<%sf'%(len(idata)/4),idata) 
                scan={"spectrum_index":result[0],
                      "scan_start_time":result[1],
                      "mzdata":mzarr,
                      "idata":iarr,
                      "mslevel":result[4]}
                if scan['mslevel']==2:
                    scan.update({'charge':result[6], 'parentmz':result[5]})
                return scan

    def getMS2ForFeature(self, featureid, ms2win=2.0):
        '''getMS2ForFeature(featureid, ms2win=2.0)
            retrieves all the MS2 spectra scan indexes which overlap the feature
            specidlist= getMS2ForFeature(feature_table_id, ms2win=2.0)
            ms2win is the window width for ion sampling - this method allows the precursor to be up to mswin/2 before the start of the identified feature. 
        '''
        sql="select spectrum_index from spectrum s inner join MSMS_precursor p on p.spectrum_spectrum_id=s.spectrum_id inner join (select mzmin, mzmax, rtmin, rtmax, msrun_msrun_id from feature f inner join convexhull_edges ce on ce.feature_feature_table_id=feature_table_id where feature_table_id=%s) f on s.msrun_msrun_id=f.msrun_msrun_id and s.scan_start_time between rtmin and rtmax and p.ion_mz between mzmin-%s and mzmax and s.ms_level=2"
        si=[]
        
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            cursor=fillDatabase.connect.cursor
            cursor.execute(sql,(featureid, ms2win/2.0))
            si=[x[0] for x in cursor.fetchall()]
        return si

    def scanToMGF(self, scannumber, thresh=0, parentmass=None, charge=None, title=''):
        '''scanToMGF(scannumber, thresh=0, parentmass=None, charge=None, title='')
        retrieve an MS2 scan and output as MGF'''
        scandata=self._getscan(scannumber)
        if scandata==None:
            return ''
        if scandata['mslevel']!=2:
            raise Exception("Only MS2 scans can be exported as MGF. %s is ms level %s"%(scannumber, scandata['mslevel']))
        return _asMGF(scandata, thresh, parentmass, charge, title)

    def _asMGF(self, scandata, thresh=0, parentmass=None, charge=None, title=''):
        maxi=0
        for p in scandata['idata']:
            if p > maxi:
                maxi=p
        mz_i=zip(scandata['mzdata'], scandata['idata'])
        mz_i_filt=[]
        for p in mz_i:
            if p[1]>maxi*thresh:
                mz_i_filt.append(p)
        if parentmass==None:
            parentmass=scandata['parentmz']
        if charge==None:
            charge=scandata['charge']
        if title!='':
            title=title+' '
        mgf=["BEGIN IONS"]
        mgf.append("TITLE=%sRun: %s Scan: %s RT: %s"%(title,self.runtag, scandata['spectrum_index'], scandata["scan_start_time"]))
        mgf.append("CHARGE=%s+"%charge)
        mgf.append("PEPMASS=%s"%parentmass)
        mgf.append("RTINSECONDS=%s"%scandata['scan_start_time'])
        mgf.append("SCANS=%s"%scandata['spectrum_index'])
        for p in mz_i_filt:
            mgf.append("%s %s"%p)
        mgf.append("END IONS")

        return "\n".join(mgf)+"\n\n"
        

    def featureRatioPH(self, feature1, feature2, optimiseRTFit=False, ions=4, tolerance=0.001, threshold=0.01):
        '''featureRatioPH( feature1, feature2, optimiseRTFit=False, ions=4, tolerance=0.001, threshold=0.01)
        feature1, feature2 are feature_table_id
        ions is the number of isotope states to consider.
        Calculate correlation between features
        Identify feature max and min RT, and scans
        Identify base (13C0) peak for each feature.
        for each scan collect f1, f2 pairs for each isotope - max peak height in window?
        calculate correlation and gradient - least squares? must pass through 0
        if optimiseRTFit: 
            shift features by a number of scans and repeat.
            Look for maximum correlation distance.
        '''
        fsql="select feature_table_id, charge, rtmin, rtmax, mzmin as mz, msrun_msrun_id as runid from feature inner join convexhull_edges on feature_feature_table_id=feature_table_id where feature_table_id=%s"
        f1={}
        f2={}
        scans={}
        # retrieve feature details
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            cursor=fillDatabase.connect.cursor
            cursor.execute(fsql, (feature1,))
            result=cursor.fetchone()
            f1={"id": result[0], "charge":result[1], "minrt":result[2], "maxrt":result[3], "mz": result[4], 'runid':result[5]}
            cursor.execute(fsql, (feature2,))
            result=cursor.fetchone()
            f2={"id": result[0], "charge":result[1], "minrt":result[2], "maxrt":result[3], "mz": result[4], 'runid':result[5]}
       
        # retrieve scans covering the features and calculate peak heights
        # inefficient but just repeat for each feature
        print 'processing feature 1'
        scan=self.getMS1Scan(rt=f1['minrt'], rtrel='less', runid=f1['runid'])
        while scan['scan_start_time']<f1['maxrt']:
            #set index value and move to mz just before minmz.
            #read back from mz reading max until 2 consecutive drops.
            #read forward from mz reading max until 2 consecutive drops.
            mini=0
            isotopes=[]
            print 'reading scan %s'%scan['spectrum_index']
            for iso in range(ions):
                isotopes.append(0)
                targetmz=f1['mz']+float(iso/f1['charge'])
                maxi=len(scan['mzdata'])
                index=int(maxi/2)
                while maxi-mini>1:
                    if scan['mzdata'][index]>targetmz:
                        maxi=index
                    else:
                        mini=index
                    index=int((maxi+mini)/2)
                maxint=scan['idata'][index]
                maxmz=index
                i=index
                d=0
                while d<2 and abs(scan['mzdata'][i] - targetmz) <tolerance:
                    i=i-1
                    if scan['idata'][i] >maxint:
                        maxint=scan['idata'][i]
                        maxmz=i
                    else:
                        d=d+1
                i=index
                d=0
                while d<2 and abs(scan['mzdata'][i] - targetmz) <tolerance:
                    i=i+1
                    if scan['idata'][i] >maxint:
                        maxint=scan['idata'][i]
                        maxmz=i
                    else:
                        d=d+1
                mini=maxmz
                isotopes[iso]=maxint
            try:
                f1['rt'].append(scan['scan_start_time'])
            except:
                f1['rt']=[scan['scan_start_time']]
            try:
                f1['peaks'].append(isotopes)
            except:
                f1['peaks']=[isotopes]
            scan=self.getMS1Scan(rt=scan['scan_start_time'], runid=f1['runid'])
        print "finished feature 1"
        print 'processing feature 2'
        scan=self.getMS1Scan(rt=f2['minrt'], rtrel='less', runid=f2['runid'])
        fmax=0

        while scan['scan_start_time']<f2['maxrt']:
            #set index value and move to mz just before minmz.
            #read back from mz reading max until 2 consecutive drops.
            #read forward from mz reading max until 2 consecutive drops.
            mini=0
            isotopes=[]
            for iso in range(ions):
                isotopes.append(0)
                targetmz=f2['mz']+float(iso/f2['charge'])
                maxi=len(scan['mzdata'])
                index=int(maxi/2)
                while maxi-mini>1:
                    if scan['mzdata'][index]>targetmz:
                        maxi=index
                    else:
                        mini=index
                    index=int((maxi+mini)/2)
                maxint=scan['idata'][index]
                maxmz=index
                i=index
                d=0
                while d<2 and abs(scan['mzdata'][i] - targetmz) <tolerance:
                    i=i-1
                    if scan['idata'][i] >maxint:
                        maxint=scan['idata'][i]
                        maxmz=i
                    else:
                        d=d+1
                i=index
                d=0
                while d<2 and abs(scan['mzdata'][i] - targetmz) <tolerance:
                    i=i+1
                    if scan['idata'][i] >maxint:
                        maxint=scan['idata'][i]
                        maxmz=i
                    else:
                        d=d+1
                mini=maxmz
                isotopes[iso]=maxint
                if maxint>fmax:
                    fmax=maxint
            try:
                f2['rt'].append(scan['scan_start_time'])
            except:
                f2['rt']=[scan['scan_start_time']]
            try:
                f2['peaks'].append(isotopes)
            except:
                f2['peaks']=[isotopes]
            scan=self.getMS1Scan(rt=scan['scan_start_time'], runid=f2['runid'])
        print 'finished feature 2'    
        # so now we have two sets of peaks of indeterminate length with associated retention times
        # simple regression -> gradient=ave(xy)/ave(x*x)
        # correlation (R^2)=1-SSerr/SStot
        # SStot = sum((y-ave(y))2)
        # SSerr = sum((y-fit(y))2)
        
        correlations=[]
        # difference in peak widths (rt)
        diff=abs(len(f1['rt'])-len(f2['rt']))
        scanc=min(len(f1['rt']), len(f2['rt']))
        s1=0
        s2=0
        if len(f1['rt'])<len(f2['rt']):
            s1=1
        else:
            s2=1
        bestfit=0
        bestrsq=0
        for d in range(diff+1):
            p1=[]
            p2=[]
            for s in range(scanc-diff):
                print "comparing peaks at relative scan %s and %s"%((d*s1)+s,(d*s2)+s )
                p1.extend(f1['peaks'][(d*s1)+s])
                p2.extend(f2['peaks'][(d*s2)+s])
            peaks=zip(p1,p2)
            pfilt=[]
            sumx=0
            sumy=0
            sumxy=0
            sumxx=0
            pcount=0
            for p in peaks:
                if min(p)>fmax*threshold:
                    pfilt.append(p)
                    pcount=pcount+1
                    sumx=sumx+p[0]
                    sumy=sumy+p[1]
                    sumxy=sumxy+(p[0]*p[1])
                    sumxx=sumxx+(p[0]*p[0])
            ratio=sumxy/sumxx
            meany=sumy/pcount
            sstot=0
            sserr=0
            print '%s: %s'%(meany,ratio) 
            for p in pfilt:
                print '%s %s'%p
                sstot=sstot+((meany-p[1])*(meany-p[1]))
                sserr=sserr+(((p[0]*ratio)-p[1])*((p[0]*ratio)-p[1]))
            rsq=1-(sserr/sstot)
            correlations.append({"rsq":rsq, "ratio":ratio, "delta_rt":f1['rt'][d*s1]-f2['rt'][d*s2], "isotopes":len(pfilt)})
            if rsq>bestrsq:
                bestrsq=rsq
                bestfit=d

        return ({"correlation":bestrsq, "bestfit": correlations[bestfit], "trials":correlations})
            
    def plotFeature(self, featureid, outfile=None, xrot=20, yrot=-45, ms2win=2.0, rtmargin=2, mzmargin=0.5, ylim=None, filter=False):
        '''plotFeature(featureid, outfile=None, xrot=20, yrot=-45, ms2win=2.0, rtmargin=2, mzmargin=0.5, ylim=None, filter=False)
        utility function to plot a feature
        #def plot3d ( msdata, msmsruns=[], features=[], outfile='plot.pdf', show=False, xrot=30, yrot=-45, featcols=['r','g','b','m','c','k'], thresh=100, ms2win=2.0, rtwindow=20.0, plotms2=True, bounds=(None, None,None,None), maxint=0):
        
        msdata is a tuple of arrays in the order mz, rt, intensity. msmsdata is an array of ms2 features. 
        bounds is the bounding box as a tuple (minmz, maxmz, minrt, maxrt)
        maxint is the peak intensity
        '''
        if outfile==None:
            outfile="%s.pdf"%featureid
        fsql="select feature_table_id, charge, rtmin, rtmax, mzmin, mzmax, msrun_msrun_id from feature inner join convexhull_edges on feature_feature_table_id=feature_table_id where feature_table_id=%s"
        f1={}
        msms=[]
        mzlist=[]
        rtlist=[]
        intlist=[]
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            cursor=fillDatabase.connect.cursor
            cursor.execute(fsql, (featureid,))
            result=cursor.fetchone()
            f1={"id": result[0], "charge":result[1], "minrt":result[2], "maxrt":result[3], "mzmin": result[4], "mzmax":result[5], "runid":result[6]}
        ssql="select spectrum_index, scan_start_time, ms_level, binary_data_mz, binary_data_rt, ion_mz, peak_intensity, total_ion_current, charge_state from spectrum left outer join MSMS_precursor on spectrum_id=spectrum_spectrum_id where msrun_msrun_id=%s and spectrum_index between %s and %s order by scan_start_time asc"
        ymin=f1['minrt']
        ymax=f1['maxrt']
        xmin=f1['mzmin']
        xmax=f1['mzmax']
        rtmin=ymin-rtmargin
        rtmax=ymax+rtmargin
        mzmin=f1['mzmin']-mzmargin
        mzmax=f1['mzmax']+mzmargin

        zval=100
        scan=self.getMS1Scan(rt=rtmin, runid=f1['runid'])
        startspec=scan['spectrum_index']
        #print "Scanstart %s rtmin %s ymin %s"%(scan['scan_start_time'], rtmin, ymin)
        scan=self.getMS1Scan(rt=rtmax, rtrel='less', runid=f1['runid'])
        endspec=scan['spectrum_index']
        #print "Scanend %s rtmax %s ymax %s"%(scan['scan_start_time'], rtmax, ymax)
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            cursor=fillDatabase.connect.cursor
            cursor.execute(ssql, (f1['runid'],startspec, endspec))
            maxint=0
            for p in cursor.fetchall():
                (index, rt, level, mzraw, rtraw, premz, intensity,tic,charge)=p
                if level==2:
                    #        msmsruns.append({"total ion current": feat['total ion current'], 'parent m/z': feat['MS:1000744'], 'charge': feat['MS:1000511'],'scan time': feat['scan time']*60}) 
                    if premz >mzmin-ms2win and premz<mzmax:         
                        msms.append({"total ion current": tic/100, 'parent m/z': premz, 'charge': charge,'scan time':rt})
                else:
                     mzdata=b64decode(mzraw.encode('utf-8'))
                     idata=b64decode(rtraw.encode('utf-8'))
                     mzarr=unpack('<%sd'%(len(mzdata)/8),mzdata) 
                     iarr=unpack('<%sf'%(len(idata)/4),idata)
                     index=0
                     rta=[]
                     mza=[]
                     ia=[]
                     if filter:
                         ions=int((f1['mzmax']-f1['mzmin'])*f1['charge']+1)
                         c13=0.0
                         #print "mzmin %s mzmax %s charge %s ions %s: %s"%(f1['mzmax'],f1['mzmin'],f1['charge'],ions,(1.0/f1['charge']))
                         peaks=[]
                         while c13<ions:
                             while mzarr[index]<f1['mzmin']+(c13/f1['charge']):
                                 index=index+1
                             #print "index at %sC13 is %s [%s]"%(c13,index,mzarr[index])
                             while iarr[index]<iarr[index-1] and mzarr[index]>f1['mzmin']+(c13/f1['charge'])-0.02 :
                                 index=index-1
                             while iarr[index]<iarr[index+1] and mzarr[index]<f1['mzmin']+(c13/f1['charge'])+0.02:
                                 index=index+1
                             peak=index
                             while iarr[index]>iarr[index-1] and mzarr[index]>f1['mzmin']+(c13/f1['charge'])-0.02:
                                 index=index-1
                             peakstart=index
                             while index < peak or (iarr[index]  >iarr[index+1] and mzarr[index]<f1['mzmin']+(c13/f1['charge'])+0.02):
                                 index=index+1
                             peakend=index
                             peaks.append((peakstart, peak, peakend))
                             c13=c13+1
                         index=0
                         #print "peaks %s"%peaks
                         while index<len(mzarr) and mzarr[index]<mzmin:
                             index=index+1
                         for p in peaks:
                             while index<p[0]:
                                 rta.append(rt)
                                 mza.append(mzarr[index])
                                 ia.append(0)
                                 index=index+1
                             while index<=p[2]:
                                 rta.append(rt)
                                 mza.append(mzarr[index])
                                 ia.append(iarr[index])
                                 if iarr[index]>maxint:
                                     maxint=iarr[index]
                                 index=index+1
                         while index<len(mzarr) and mzarr[index]<mzmax:
                             rta.append(rt)
                             mza.append(mzarr[index])
                             ia.append(0)
                             index=index+1        
                     else:
                         while index<len(mzarr) and mzarr[index]<mzmax:
                             if mzarr[index] > mzmin:
                                 rta.append(rt)
                                 mza.append(mzarr[index])
                                 ia.append(iarr[index])
                                 if iarr[index]>maxint:
                                     maxint=iarr[index]
                             index=index+1
                     mzlist.append(mza)
                     rtlist.append(rta)
                     intlist.append(ia)
        ys=[ymin, ymax, ymax, ymin,ymin]
        zs=[zval,zval,zval,zval,zval]
        xs=[xmin,xmin,xmax,xmax,xmin]
        #return ( (mzlist,rtlist, intlist), msms, [[xs,ys,zs,1],], outfile,  (mzmin,mzmax, rtmin,rtmax), maxint)
        
        mi=maxint
        if ylim !=None:
            mi=ylim
        MSPlot.msplot3d.plot3d_data( (mzlist,rtlist, intlist), msms, featuredata=[[xs,ys,zs,1],], outfile=outfile,  bounds=(mzmin,mzmax, rtmin,rtmax,), maxint=mi, xrot=xrot, yrot=yrot, ms2win=ms2win)
            
        
    def silacPairMA(self, types=[], tag=None):
        '''
        Retrieve a list of feature pairs of certain types where the experiment tag is tag
        list=silacPairMA( types=[], tag=None)
        types is a list of feature_group_type id
        tag is the experiment label given to the feature pairs
        '''
        if tag==None or len(types)==0:
            raise Exception("parameters must be supplied to retrieve ratios")
        sql="select distinct feature_low_id as `low id`, a.intensity as `low intensity`, ace.mzmin as `low mzmin`, ace.mzMax as `low mzmax`, ace.rtMin as `low rtmin`, ace.rtMax as `low rtmax`, a.charge as `low charge`, ifnull(asp.spectra,0) as 'L MS2', feature_high_id as `high id`, b.intensity as `high intensity`, bce.mzmin as `high mzmin`, bce.mzMax as `high mzmax`, bce.rtMin as `high rtmin`, bce.rtMax as `high rtmax`, b.charge as `high charge`,ifnull(bsp.spectra,0) as 'H MS2',b.intensity/a.intensity as ratio, fg.feature_group_name from feature_pair fp inner join feature a on a.feature_table_id=feature_low_id inner join convexhull_edges ace on ace.feature_feature_table_id=a.feature_table_id inner join feature b on b.feature_table_id=feature_high_id inner join convexhull_edges bce on bce.feature_feature_table_id=b.feature_table_id inner join feature_group_type fg on fp.feature_group_id = fg.feature_group_id left outer join (select feature_feature_table_id, count(*) as spectra from feature_has_MSMS_precursor group by feature_feature_table_id) asp on asp.feature_feature_table_id=a.feature_table_id left outer join (select feature_feature_table_id, count(*) as spectra from feature_has_MSMS_precursor group by feature_feature_table_id) bsp on bsp.feature_feature_table_id=b.feature_table_id where a.msrun_msrun_id = %s and b.msrun_msrun_id = %s and experiment=%s and fp.feature_group_id in %s"
        table=[("L id","L intensity","L mzmin","L mzmax","L rtmin","L rtmax","L charge","L MS2","H id","H intensity","H mzmin","H mzmax","H rtmin","H rtmax","H charge", "H MS2","ratio", "Pair type")]
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            cursor=fillDatabase.connect.cursor
            cursor.execute(sql, (self.runid,self.runid, tag, types))
            for res in cursor.fetchall():
                table.append(res)
            
        return table

    def listUnidentifiedFeatures(self, runtag, withMS2=False, count=0, peptidescore=0.0, searchgroup=0):
        '''listUnidentifiedFeatures(runtag, withMS2=False, count=0, peptidescore=0.0, searchgroup=0)
        retrieves a table of features which have not got an identification
so that an inclusion list can be built.
runtag: The label used for the consensus feature
withMS2: (default False) include features with MS2 but no identifications
count: maximum number of entries to return (ordered by intensity)
peptidescore: (default 0.0) set a lower limit on the peptidescore (not relevant if withMS2 is False)

Returns a table with columns: consensus feature id, intensity, charge, mz, min RT (seconds), max RT (seconds)
'''
        sqlMS2=  "select acf.cf_id, acf.intensity, acf.charge, min(ce.mzmin) as mz, min(ce.RTmin) as minRT, max(ce.RTmax) as maxRT  from consensus_feature acf inner join consensus_feature_element cfe on cfe.consensus_id = acf.cf_id inner join convexhull_edges ce on ce.feature_feature_table_id=cfe.feature_id  where acf.runtag=%s and acf.cf_id not in (  select cf_id from consensus_feature cf inner join consensus_feature_element cfe on cfe.consensus_id = cf.cf_id inner join feature_has_MSMS_precursor mp on mp.feature_feature_table_id=cfe.feature_id inner join MASCOT_peptide pep on pep.precursor_precursor_id= mp.MSMS_precursor_precursor_id inner join convexhull_edges ce on ce.feature_feature_table_id=cfe.feature_id  where cf.runtag=%s and pep.pep_score > %s) group by acf.cf_id, acf.intensity order by intensity desc"
        sqlnoMS2="select acf.cf_id, acf.intensity, acf.charge, min(ce.mzmin) as mz, min(ce.RTmin) as minRT, max(ce.RTmax) as maxRT  from consensus_feature acf inner join consensus_feature_element cfe on cfe.consensus_id = acf.cf_id inner join convexhull_edges ce on ce.feature_feature_table_id=cfe.feature_id  where acf.runtag=%s and acf.cf_id not in (  select cf_id from consensus_feature cf inner join consensus_feature_element cfe on cfe.consensus_id = cf.cf_id inner join feature_has_MSMS_precursor mp on mp.feature_feature_table_id=cfe.feature_id inner join convexhull_edges ce on ce.feature_feature_table_id=cfe.feature_id  where cf.runtag=%s) group by acf.cf_id, acf.intensity order by intensity desc"
        
        sql=sqlnoMS2
        sqlpar=[runtag,runtag]
        if withMS2==True:
            sql=sqlMS2
            sqlpar.append(peptidescore)
        if count>0:
            sql=sql+ " limit %s"%count
        result=[]
        try:
            with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
                fillDatabase = database.FillDatabase(sqlCon, self.runtag)
                cursor=fillDatabase.connect.cursor
                cursor.execute(sql,sqlpar)
                for r in cursor.fetchall():
                    result.append([int(r[0]), float(r[1]), int(r[2]), float(r[3]), float(r[4]), float(r[5])])
        except Exception, e:
            raise Exception("Error building list from database: %s"%e)
        return result

    def listMSSearch(self):
        '''listMSSearch()
        returns a list of MSSearch ID, peptide hits, and the search group 
        for the current msrun'''
        sql="select distinct dbs.db_search_id, dbsg.db_search_group_id, dbsg.db_search_group_name, dbsg.db_search_group_description, dbsg.db_search_engine from spectrum s inner join MSMS_precursor pre on pre.spectrum_spectrum_id=s.spectrum_id inner join MASCOT_peptide pep on pre.precursor_id=pep.precursor_precursor_id inner join db_search dbs on pep.db_search_id=dbs.db_search_id inner join db_search_group dbsg on dbsg.db_search_group_id=dbs.db_search_group_id where s.msrun_msrun_id=%s"%self.runid
        searches=[]
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            cursor=fillDatabase.connect.cursor
            cursor.execute(sql)
            for r in cursor.fetchall():
                searches.append({"searchid":r[0],"searchgroupid":r[1], "searchgroupname":r[2], "searchgroupdescription":r[3], "searchgroupengine":r[4]}) 
        return searches
                


    def calculateFDR(self, mssearchid, reverseprefix='REV_', level=0.01):
        '''calculateFDR( mssearchid, reverseprefix='REV_', level=0.01)
        calculates the FDR for search mssearchid at level (default 1%) 
        where reversed sequences are prefixed with reverseprefix.'''
        sql="select min(pep_score) from (select pep_score, fp/psm as fpr from (select if( protein_accession like '%s%%', 1+@fp:=@fp+1, @fp) as fp, 1+@tp:=@tp+1 as psm, pep_score, protein_accession from ( select pep_score, protein_accession from MASCOT_peptide p inner join db_search db on p.db_search_id=db.db_search_id inner join MASCOT_protein pr on pr.mascot_peptide_peptide_id=p.peptide_id where db.db_search_id=%s order by pep_score desc ) as a ) as p  having fpr < %s) as q"%(reverseprefix,mssearchid,level)
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            cursor=fillDatabase.connect.cursor
            cursor.execute('set @fp:=0')
            cursor.execute('set @tp:=0')
            cursor.execute(sql)
            r=cursor.fetchone()
            return float(r[0])

    def getMSProteins(self, mssearchlist, threshold, peptidecount=1, exclude=['REV_', 'CON_'], totalpep=False, distinct=False):
        '''getMSProteins(mssearchlist, threshold, peptidecount=1)
        retrieve a list of unique proteins for the searches in mssearchlist 
        with the cutoffs in threshold. 
        In each search at least peptidecount peptides with a score over 
        threshold must be identified unless totalpep is set in which case 
        peptidecount is taken over all searches.
        If distinct is set then only one occurrence of (sequence,mods) is 
        counted per search.
        '''
        if len(mssearchlist)==0:
            raise Exception("No searches specified")
        
        if len(mssearchlist) != len(threshold):
            raise Exception("search id count and threshold count do not match")
        
        if len(exclude) >0:
            excludes="and "+" and ".join(["protein_accession not like '%s%%'"%x for x in exclude])
        distpep='mascot_peptide_peptide_id'
        if distinct:
            distpep='distinct pep_seq, pep_var_mod'
        searches=" or ".join(["(db_search_id=%s and pep_score > %s)"%(x[0],x[1]) for x in zip(mssearchlist, threshold)])
        sql="select distinct protein_accession, max(peptides) as peptides, count(db_search_id) as searches from (select distinct protein_accession, count("+distpep+") as peptides, db_search_id from MASCOT_protein inner join MASCOT_peptide on mascot_peptide_peptide_id=peptide_id where  (%s) %s group by db_search_id, protein_accession having peptides >= %s)a group by protein_accession"%(searches, excludes, peptidecount)
        tpsql="select distinct protein_accession, sum(peptides) as peptides, count(db_search_id) as searches from (select distinct protein_accession, count("+distpep+") as peptides, db_search_id from MASCOT_protein inner join MASCOT_peptide on mascot_peptide_peptide_id=peptide_id where  (%s) %s group by db_search_id, protein_accession )a group by protein_accession having peptides >= %s"%(searches, excludes, peptidecount)
        proteins=[]
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            cursor=fillDatabase.connect.cursor
            if totalpep:
                cursor.execute(tpsql)
            else:
                cursor.execute(sql)             
            for r in cursor.fetchall():
                proteins.append({"accession":r[0], "peptides":r[1], "searches": r[2]})
                
        return proteins

    def getMSPeptides(self, mssearchlist, threshold, exclude=['REV_', 'CON_']):
        '''getMSPeptides(mssearchlist, threshold, peptidecount=1)
        retrieve a list of peptides for the searches in mssearchlist 
        with the cutoffs in threshold.         
        '''
        if len(mssearchlist)==0:
            raise Exception("No searches specified")
        
        if len(mssearchlist) != len(threshold):
            raise Exception("search id count and threshold count do not match")
        
        if len(exclude) >0:
            excludes="and "+" and ".join(["protein_accession not like '%s%%'"%x for x in exclude])
        
        searches=" or ".join(["(db_search_id=%s and pep_score > %s)"%(x[0],x[1]) for x in zip(mssearchlist, threshold)])
        sql="select distinct protein_accession, pep_seq, pep_var_mod, db_search_id from MASCOT_protein inner join MASCOT_peptide on mascot_peptide_peptide_id=peptide_id where  (%s) %s"%(searches, excludes)
        
        peptides=[]
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            cursor=fillDatabase.connect.cursor
            cursor.execute(sql)             
            for r in cursor.fetchall():
                peptides.append({"accession":r[0], "peptide":r[1], "mods": r[2],"searchid":r[3] })
                
        return peptides

    def dbQuery(self, sql,params=()):
        'dbQuery(sql, params=()) - run an sql query on the pymsa database.'
        with database.ConnectMySQL(self.host, self.user, self.password,self.database) as sqlCon:      
            fillDatabase = database.FillDatabase(sqlCon, self.runtag)
            cursor=fillDatabase.connect.cursor
            cursor.execute(sql, params)             
            return cursor.fetchall()
