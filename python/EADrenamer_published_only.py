import os,glob,sys,re
import xml.etree.ElementTree as ET

#src=sys.argv[1]
#dst=sys.argv[2]
src = raw_input("Source Directory with trailing slash: ")
dst = raw_input("Destination Directory (must exist) with trailing slash: ")

os.chdir(src)

for files in glob.glob("*.xml"):
		content = ET.parse(files)
		namespace = "{urn:isbn:1-931666-22-9}"
		eadid = content.find('.//{0}eadid'.format(namespace)).text
		findaidstatus = content.find(".//{0}eadheader[@findaidstatus='published']".format(namespace))
		if findaidstatus:
			if eadid:
				newfilename = eadid #get the new file name
			try:
				os.rename(files, dst + newfilename+".xml")
			except Exception,e:
				print e
			else:
				print "%s renamed to %s.xml" %(files,newfilename)
		else: 
			print "%s findaidstatus is not set to 'published'"