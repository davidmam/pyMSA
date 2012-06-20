
# This script is run during 'make html'. It adds api linking to index.html, example scripts.html and api documentation.html. __file__ is used for locations to get correct relative path. 


# changes py-modindex.html to ../../../api doc.html in index html. This will make the module index point to the api docs. 

import os

fileOpen = open(__file__.rstrip('apiLinking.py')+'index.html','r')
outFile = open(__file__.rstrip('apiLinking.py')+'index_temp.html', 'w')
for line in fileOpen:
	line = line.replace('py-modindex.html', '../../../api doc.html')
	outFile.write(line)

outFile.close()
os.rename(__file__.rstrip('apiLinking.py')+'index_temp.html', __file__.rstrip('apiLinking.py')+'index.html')


# adds <meta HTTP-EQUIV="REFRESH" content="0; url=manual/_build/html/index.html"> to top of example scripts.html and api documentation.html

fileOpen = open(__file__.rstrip('apiLinking.py')+'3. Example scripts.html','r')
outFile = open(__file__.rstrip('apiLinking.py')+'3. Example scripts_temp.html', 'w')
outFile.write('<meta HTTP-EQUIV="REFRESH" content="0; url=../../../api/html/example_scripts-module.html">')
for line in fileOpen:
	outFile.write(line)

outFile.close()
os.rename(__file__.rstrip('apiLinking.py')+'3. Example scripts_temp.html', __file__.rstrip('apiLinking.py')+'3. Example scripts.html')




fileOpen = open(__file__.rstrip('apiLinking.py')+'5. API documentation.html','r')
outFile = open(__file__.rstrip('apiLinking.py')+'5. API documentation_temp.html', 'w')
outFile.write('<meta HTTP-EQUIV="REFRESH" content="0; url=../../../api doc.html">')
for line in fileOpen:
	outFile.write(line)

outFile.close()
os.rename(__file__.rstrip('apiLinking.py')+'5. API documentation_temp.html', __file__.rstrip('apiLinking.py')+'5. API documentation.html')
