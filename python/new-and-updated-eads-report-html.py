import sys, os, glob
import requests
import json
import re
import ConfigParser
import time
import datetime
import csv


# Script generates a report of new and updated finding aids (and counts) since the date specified using a very convoluted process that only makes sense at Duke
# Script takes as input a .txt file with a list of new EADIDs, the path to published EADs at Duke,the beginning date of the quarter, and a destination path to save the report.


# local config file, contains variables
configFilePath = 'local_settings.cfg'
config = ConfigParser.ConfigParser()
config.read(configFilePath)

# URL parameters dictionary, used to manage common URL patterns
dictionary = {'baseURL': config.get('ArchivesSpace', 'baseURL'), 'repository':config.get('ArchivesSpace', 'repository'), 'user': config.get('ArchivesSpace', 'user'), 'password': config.get('ArchivesSpace', 'password')}
baseURL = '{baseURL}'.format(**dictionary)
repositoryBaseURL = '{baseURL}/repositories/{repository}/'.format(**dictionary)

new_eads_list = raw_input('Path to EADID List CSV: ')

current_eads_path = raw_input('Path to published EADs: ')

# authenticates the session
auth = requests.post('{baseURL}/users/{user}/login?password={password}&expiring=false'.format(**dictionary)).json()
session = auth["session"]

#if auth.status_code == 200:
print "Authenticated!"
headers = {'X-ArchivesSpace-Session':session}

#set EAD export options: number components and include DAOs
export_options = '?include_daos=true&numbered_cs=true&include_unpublished=false'

#today's date
today_date = datetime.datetime.today().strftime('%Y-%m-%d')

quarter_start_date = raw_input("Quarter Start Date: ")

#location to store text file of report
destination = raw_input('Save report to: ')
f = open(destination+'new-ead-report'+today_date+'.html', 'w')

f.write("<html><head><h1>Finding Aid Report</h1></head><body><p><a href=\"#new\">New Finding Aids</a> | <a href=\"#updated\">Updated Finding Aids</a></p><h2><a name=\"new\"></a>New Finding Aids Posted Since {0}</h2>".format(quarter_start_date))

# Exports EAD for all resources matching EADID input repository

with open(new_eads_list,'rb') as csvfile:
    reader = csv.reader(csvfile)
    #next(csvfile, None) #ignore header row
    print "writing new finding aids to file..."
    new_count = 0
    for row in reader:
		new_count = new_count + 1
		eadid = row[0]

#advanced search for EADID
		results = (requests.get(repositoryBaseURL + '/search?page=1&aq={\"query\":{\"field\":\"ead_id\",\"value\":\"'+eadid+'\",\"jsonmodel_type\":\"field_query\",\"negated\":false,\"literal\":false}}', headers=headers)).json()

#Make sure the EADID input matches an EADID value in ASpace
		if results["total_hits"] is not 0:
			#get the URI of the first search result (should only be one)
			uri = results["results"][0]["id"]
			#get JSON for the resource based on above URI
			resource_json = (requests.get(baseURL + uri, headers=headers)).json()
			#print resource_json
			#get URI of Resource record
			resource_uri = resource_json["uri"]

#stuff for report
			#get title
			finding_aid_title = resource_json["finding_aid_title"].replace("\n","").encode('utf8')
			#print "Title: " + finding_aid_title
			#extent
			extent_number = resource_json["extents"][0]["number"]
			extent_type = resource_json["extents"][0]["extent_type"]
			#print "Extent: " + extent_number, extent_type
			#get finding aid link
			ead_location = resource_json["ead_location"]
			#print "URL: " + ead_location
			#print abstract
			notes = resource_json["notes"]
			for note in notes:
				if note["type"] == "abstract":
						abstract = note["content"][0].encode('utf8')
			#			print "Abstract: " + abstract
			#finding_aid_date = resource_json["finding_aid_date"]
			#finding_aid_author = resource_json["finding_aid_author"]
			#print "Processor: " + finding_aid_author
			#Center information?
			#print ""
			#also write to txt file
			f.write("<div><h3><a href=\"{3}\">{0}</a> ({1} {2})</h3><p>{4}</p><hr></div>".format(finding_aid_title, extent_number, extent_type, ead_location, abstract))

f.write("<h2><a name=\"updated\"></a>Finding Aids Updated Since {0}</h2>".format(quarter_start_date))

#Read over EAD directory and get files modified after specified date. Then, get finding aid URLs out of ASpace
for root, dirs, filenames in os.walk(current_eads_path):
	print "writing updated finding aids to file..."
	update_count = 0
	for filename in filenames:
		filepath = os.path.join(root, filename)
		eadid = filename.replace(".xml","")
		modified_time = os.path.getmtime(filepath)
		modified_time_iso = datetime.datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d')

		if modified_time_iso >= quarter_start_date:
			update_count = update_count + 1
			results = (requests.get(repositoryBaseURL + '/search?page=1&aq={\"query\":{\"field\":\"ead_id\",\"value\":\"'+eadid+'\",\"jsonmodel_type\":\"field_query\",\"negated\":false,\"literal\":false}}', headers=headers)).json()
			if results["total_hits"] is not 0:
				#get the URI of the first search result (should only be one)
				uri = results["results"][0]["id"]
				resource_json = (requests.get(baseURL + uri, headers=headers)).json()
				ead_location = resource_json["ead_location"]
				finding_aid_title = resource_json["finding_aid_title"].replace("\n","").encode('utf8')
				f.write("<div><p><a href=\"{1}\">{0}</a> (updated: {2})</p></div>".format(finding_aid_title, ead_location, modified_time_iso))

f.write("<p>TOTAL NEW: {0}<br/>TOTAL UPDATED: {1}</p></body></html>".format(new_count, update_count))
f.close

print "All Done!!"
