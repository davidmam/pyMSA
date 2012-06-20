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
Multiple classes to write information to output. 
"""

# author: ndeklein
# date:08/02/2012
# summary: Writes readerInstance (from parseFeatureXML.Reader) to output files.

import csv
import collections 
import mzmlFunctions
import copy
import sys
import config
import pymzml
import itertools
configHandle =  config.ConfigHandle()
config = configHandle.getConfig()

class CsvWriter:
	"""
	BaseClass for writing information to a .csv file.
	"""
	def csvWriteLine(self, lineList):
		r"""
		csvWriteLine writes one line to an open csvFile. The column values of that row are the elements in the given list (each element is the value of one column).
		
		@type lineList: list
		@param lineList: A list of values for each column of the row
		@raise TypeError: lineList is not of type list 

		B{Example}:

		Write a small csv filesv:
				
		>>> columnHeaderList = ['spectrum_index','spectrum_native_id','charge']
		>>> columnExampleValues = [[1, f_3194894, 2], [2, f_4938928, 2], [3,f_9234892, 4]] # this is a list of lists, each list standing for one line
		>>> with FileWriter(example_output.csv') as fw:   # FileWritere is used to open the file and close it after the indent goes back
		...		fw.csvWriteLine(columnHeaderList)		# before the loop, write the column headers
		...		for row in columnExampleValues:
		...			fw.csvWriteLine(row) # in every loop row is a list

		"""
		
		# because the csv writer splits strings up into single letters only lists are allowed
		# if lineList is not a list (set doesn't work either), raise typeError
		if not type(lineList) == list :
			raise TypeError, 'lineList given to csvWriteLine is not of type list. Instead is of type: '+str(type(lineList))
		# making the writer and setting the delimiter
		writer = csv.writer(self.outFile, delimiter='\t')
		# writes the line to csv file. If line is a list, it automatically seperates each element in the list with \t
		writer.writerow(lineList)
			   
# If something else has to be written than a standard text file, use outFile as the IO handler. Otherwise FileWriters write function can be used.	 
class FileWriter(CsvWriter):
	r"""
	The FileWriter class is used for generic stuff like opening and closing the file that will be written. It will
	inherit from other more specific writer functions like CsvWriter so that outFile, the variable containing the stream
	doesn't have to be passed on but can be used directly by a CsvWriter instance.
	
	@raise ValueError: The file is closed
	
	B{Example}:
	
	The scope of fw:
	
	>>> with FileWriter('example_outfile.txt') as fw:
	...		fw.outFile.write('test file for FileWrite class in output.py')  # the file is open
	...		fw.outFile.write('this writes into the same file, because it is still open')    # the file is still open
	>>> fw.outFile.write('the file is closed now') # Because this line is out of the indent of the with statement, the file is now closed
	"""
	
	def __init__(self, path):
		self.path = path
	
	# Open the file when with FileHandler is called to write binaries (wb) to the file
	def __enter__(self):
		# self.outFile can be used with every function that uses an open file, as long is it's in the "with FileHandler" indentation block  
		self.outFile = open(self.path, 'wb')
		return self
	
	# Close the file after the with statement is ended (indentation is back
	def __exit__(self, *args):
		self.outFile.close()
		
	# write a text to a file	
	def write(self, text):
		self.outFile.write(text)
		

# class to contain functions that multiple writer classes that write feature information to different formats can use
class FeatureWriter: 	
	"""
	BaseClass of all classes that write out featureXML information. 
	Has functions to easily acces data from parseFeatureXML.Reader instances
	"""

	def __init__(self, featurexmlReaderInstance):
		"""
		@type featurexmlReaderInstance: parseFeatureXML.Reader
		@param featurexmlReaderInstance: An instance of parseFeatureXML.Reader()
		
		"""
		# if FeatureWriter is called with a featurexmlReaderInstance, use this readerInstance. Can still be called from a
		# class that inherits FeatureWriter (likeFeatureCsvWriter) without having to give featurexmlReaderInstance (because it already has self.featurexmlReaderInstance in the class)
		if featurexmlReaderInstance:
			self.featurexmlReaderInstance = featurexmlReaderInstance
		
	def getInfo(self, keys):
		# use r before the documentation otherwise \t isn't recognised as special character
		r"""
		Generator function that yields featureId, key and the value of featurexmlReaderInstance[key] from all features in a given parseFeatureXML.Reader() instance. 
		
		@type keys: list
		@param keys: The names of the properties to get information from.
		@raise TypeError: Keys is not of type list

		
		B{Example}:
		
		Printing charge and intensity of all features: 
		
		>>> featurexmlReaderInstance = parseFeatureXML.Reader('example_featureXML_file.featureXML')	# get the parseFeatureXML.Reader() instance
		>>> featureWriter = FeatureWriter(featurexmlReaderInstance)									# get the FeatureWriter() instance
		>>>	print 'id\tkey\tvalue'																	# little header to make clear what is what
		>>> for featureId, key, info in featureWriter.getInfo(['charge','intensity']):				# loop through all the features and get info of 'charge' and 'intensity'
		...		print featureId+':\t'+key+'\t'+info													# print the featureId, key and info.
		id							key			value
		f_13020522388175237334: 	charge 		2
		f_13020522388175237334: 	intensity 	524284
		f_8613715360396561740: 		charge 		2
		f_8613715360396561740: 		intensity 	111329
		f_43922326584371237334: 	charge 		2
		f_43922326584371237334: 	intensity 	524284
		"""
		
		if not type(keys) == list and not type(keys) == set:
			raise TypeError, 'keys given to getInfo is not of type list or set. Instead is of type: '+str(type(keys))

		# get all the features of the featurexmlReaderInstance
		for features in self.featurexmlReaderInstance.getSimpleFeatureInfo():
			# for every key (which is every column header)
			for key in keys:
				# return the value of the featurexmlReaderInstance[key]
				yield self.featurexmlReaderInstance['id'],key, self.featurexmlReaderInstance[key]
	
# Writes information from a readerIntance to a csv file
class FeatureCsvWriter(FileWriter, FeatureWriter):
	# using r in front of doc string because otherwise \t isn't recognised
	r""" 
	Write information  of a feature Reader instance (as created by parseFeatureXML.Reader()) to a csv file
	
	"""
   
	def __init__(self, path, featurexmlReaderInstance):
		"""
		@type path: string
		@param path: Relative or absolute path and filename for the output file
		@type featurexmlReaderInstance: parseFeatureXML.Reader
		@param featurexmlReaderInstance: An instance of parseFeatureXML.Reader(). An example to get a reader file 
		
		B{Example}:
		
		Write parseFeatureXML.Reader info to a csv file
		
		>>> reader = parseFeatureXML.Reader('example_featureXML_file.featureXML)					# reader instance
		>>> featureCsvWriter = FeatureCsvWriter('example_output.csv', reader)					# write the feature csv file
		"""
		# the reader instance
		self.featurexmlReaderInstance = featurexmlReaderInstance

		# self.columnList is the sorted predefined list. 
		self.columnList = sorted(['spectrum_index','spectrum_native_id','convexhull_yCoor','convexhull_xCoor','charge','intensity','position_dim0','position_dim1','overallquality','quality_dim0','quality_dim1','id'])

		# Use the FileHandler class to open the file and close if after writing is done
		with FileWriter(path) as fw:
			# write the column headers to the csv file
			fw.csvWriteLine(self.columnList)

			#dict to story all information from the featurexmlReaderInstance. Makes a defaultdict so unknown featureIds can be added as key, and as default value
			# an ordered dict for the different info keys
			infoDict = collections.defaultdict(dict)
			
			# infolist is a list of all the keys in featurexmlReaderInstance
			self.infoList = self.featurexmlReaderInstance.getKeys()
			# for all the content in the featurexmlReaderInstance that is found with the keys in columnList
			x = 0
			
			for featureId, key, content in self.getInfo(self.infoList):
			# make the value of infodict[featureId] an ordered dict 
				infoDict[featureId][key] = content


			# for all the features in reader instance
			for featureId in infoDict:
				# for all the coordinates in the convexhull
				for points in infoDict[featureId]['convexhull']:
					# list containing the information for one row
					rowContent = []
					# adding the rows THIS ORDER IS IMPORTANT 
					#charge,  convexhull_xCoor, convexhull_yCoor, id, intensity, overallquality, retention time (s), mz, quality_dim0, quality_dim1, spectrum_index, spectrum_native_id								
					rowContent.append(infoDict[featureId]['charge'])
					rowContent.append(points['rt'])
					rowContent.append(points['mz'])
					rowContent.append(infoDict[featureId]['id'])
					rowContent.append(infoDict[featureId]['intensity'])
					rowContent.append(infoDict[featureId]['overallquality'])
					rowContent.append(infoDict[featureId]['retention time'])
					rowContent.append(infoDict[featureId]['mz'])
					rowContent.append(infoDict[featureId]['quality'][0][1])
					rowContent.append(infoDict[featureId]['quality'][1][1])
					for userParam in infoDict[featureId]['userParam']:
						if userParam['name'] == 'spectrum_native_id':
							rowContent.append(userParam['value'].split('scan=')[1])
						elif userParam['name'] == 'spectrum_index':
							rowContent.append(userParam['value'])
					fw.csvWriteLine(rowContent)


class MsrunCsvWriter(FileWriter):
	"""
	Write out information of a pymzml.run.Reader instance to a csv file
	"""
	
	# using msrun and copyMsrun because the Reader object of pymzml is set up so that it can't be copied by deepcopy or copy,
	# unless doing objs = [copy.deepcopy(obj) for obj in pymzml.run.Reader(mzmlFile)] which makes it very very slow
	# *Note* Should change it to use spec.deRef() instead of copying the whole object
	def __init__(self, path, msrun):
	# using r in front of doc string because otherwise \t isn't recognised
		r"""

		@type path: string
		@param path: path for output file
		@type msrun: pymzml.run.Reader
		@param msrun: An instance of pymzml.run.Reader()

		B{Example}:

		Write an instance of pymzml.run.Reader to a csv file:

		>>> msrun = pymzml.run.Reader('example_mzML_file.mzML')						# instance of pymzml.run.Reader
		>>> writer = MsrunCsvWriter('example_outfile.csv', msrun)					# write the csv file
		"""		

		# Use the FileHandler class to open the file and close if after writing is done
		with FileWriter(path) as fw:
			# a list of all the columns the user do not want in the ms/ms file from the configfile

			excludeList = config.get('data', 'excludeMsrunCsvColumns').strip(' ').split(',')
			# a list of all the columns the user want sin the ms/ms file from the configfile that are not in feature.keys() 
			includeList = config.get('data','includeMsrunCsvColumns').strip(' ').split(',')
			# spectrumKeys will contain the column header names
			spectrumKeys, precursorKeys, spectrumList = mzmlFunctions.getKeys(msrun, excludeList, includeList)
				
			# write the column names
			fw.csvWriteLine(list(spectrumKeys))

			# loop through the spectra that were used in mzmlFunctions.getKeys (spectrumList) and the ones left over in msrun
			# itertools.izip makes an iterator of two lists
			for spectrum in itertools.izip(spectrumList, msrun):
				if spectrum[0]['id'] != 'TIC':
					# list to contain the content for each row
					rowContent = []
					# only the keys specefied by spectrumKeys above
					for key in spectrumKeys:
						try:
							if key in precursorKeys:
								rowContent.append(spectrum[0]['precursors'][0][key])
							else:
								rowContent.append(spectrum[0][key])
						except KeyError:
							rowContent.append('N/A')
					fw.csvWriteLine(rowContent)



class CompareDataWriter(FileWriter):
	"""
	Write out compared data e.g. Msrun data (result of pymzml parsing of mzML files) compared to featureXML
	
	
	"""
	def __init__(self, path):
		"""
		@type path: string
		@param path: The path for the file to be written out
		"""
		self.path = path
	
	def precursorPerFeatureCsvWriter(self, precursPerFeature):
		r"""
		Write precursorPerFeature to a Csv file. 
		
		@type precursPerFeature: dictionary
		@param precursPerFeature: A dictionary with as key feature id and value how many precursors are found in that feature. 

		B{Example}:

		Write featureId and the amount of precursors per feature to a file:

		>>> import pymzml
		>>> import compareFeatureXMLmzML as compare
		>>> msrun = pymzml.run.Reader('example_mzML_file.mzML')						# instance of pymzml.run.Reader
		>>> precursPerFeature = compare.compareCoordinate('example_mzML_file.mzML', 'exampleFeatureXMLfile.featureXML')['featPerPrecursorDict']    # see compareFeatureXMLmzML.py for details
		>>> writer = CompareDataWriter('example_output.csv')							# instance of CompareDataWriter
		>>> writer.precursorPerFeatureCsvWriter(precursPerFeature)					# write the csv file
		"""

		# Use the FileHandler class to open the file and close if after writing is done
		with FileWriter(self.path) as fw:
			# write the column headers
			fw.csvWriteLine(['id','# precursors'])
			# for all the feature ids in featurePrecursor
			for feature in precursPerFeature:
				fw.csvWriteLine([feature, precursPerFeature[feature]])
