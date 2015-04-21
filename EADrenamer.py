import os,glob,sys,re
import xml.etree.ElementTree as ET

folder=sys.argv[1]
os.chdir(folder)

for files in glob.glob("*.xml"):
		content = ET.parse(files)
		namespace = "{urn:isbn:1-931666-22-9}"
		eadid = content.find('.//{0}eadid'.format(namespace)).text
		if eadid:
			newfilename = eadid #get the new file name
		try:
			os.rename(files, newfilename+".xml")
		except Exception,e:
			print e
		else:
			print "%s renamed to %s.xml" %(files,newfilename)