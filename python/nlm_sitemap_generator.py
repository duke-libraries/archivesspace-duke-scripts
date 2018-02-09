import os,glob,sys,re
import xml.etree.ElementTree as ET
import datetime

#Script used to generate Sitemap for contributing EADs to: https://www.nlm.nih.gov/hmd/consortium/index.html

#Script searches for terms 'medicine' and 'physician' in text of //controlaccess//text() for EAD files in input directory
#and generates sitemap of finding aid URLs and lastmod times for matching finding aids
#Written by Noah Huffman, 2/9/2018

folder = raw_input('Input directory of XMLs: ')
output_file = raw_input('path to output file: ')

os.chdir(folder)

with open(output_file, "w") as file:

		#Start writing XML file
		file.write('<?xml version="1.0" encoding="UTF-8"?>\n\t<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

		for files in sorted(glob.glob("*.xml")):
				
				content = ET.parse(files)
				namespace = "{urn:isbn:1-931666-22-9}"
				eadid = content.find('.//{0}eadid'.format(namespace))
				url = eadid.get('url')
				date = os.path.getmtime(files)
				lastmod = datetime.datetime.fromtimestamp(int(date)).strftime('%Y-%m-%d')

				try:
						controlaccess = content.find('.//{0}controlaccess'.format(namespace))
						controlaccesslist = list(controlaccess.itertext())
						textstring = ''.join(controlaccesslist)
						#print textstring
						if 'Medicine' in textstring or 'medicine' in textstring or 'Medical' in textstring or 'medical' in textstring or 'Physician' in textstring or 'physician' in textstring or 'Public health' in textstring:
							print lastmod + ' | ' + url
							file.write("\n\t\t<url>\n\t\t\t<loc>{0}</loc>\n\t\t\t<lastmod>{1}</lastmod>\n\t\t</url>".format(url, lastmod))
				except:
					pass
		file.write('</urlset>')

