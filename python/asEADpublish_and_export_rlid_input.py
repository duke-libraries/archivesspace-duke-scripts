#!/usr/bin/env python

import sys
import requests
import json
import re
import ConfigParser
import time


# local config file, contains variables
configFilePath = 'local_settings.cfg'
config = ConfigParser.ConfigParser()
config.read(configFilePath)

# URL parameters dictionary, used to manage common URL patterns
dictionary = {'baseURL': config.get('ArchivesSpace', 'baseURL'), 'repository':config.get('ArchivesSpace', 'repository'), 'user': config.get('ArchivesSpace', 'user'), 'password': config.get('ArchivesSpace', 'password')}
baseURL = '{baseURL}'.format(**dictionary)
repositoryBaseURL = '{baseURL}/repositories/{repository}/'.format(**dictionary)

# Prompt for input, a comma separated list of EADID values (e.g. johndoepapers, janedoepapers, johnandjanedoepapers)
rlids = raw_input("List of RLIDs:  ")
# Split comma separated list
rlids_list = rlids.split(",")

# authenticates the session
auth = requests.post('{baseURL}/users/{user}/login?password={password}&expiring=false'.format(**dictionary)).json()
session = auth["session"]

#if auth.status_code == 200:
print "Authenticated!"
headers = {'X-ArchivesSpace-Session':session}

#set EAD export options: number components and include DAOs
export_options = '?include_daos=true&numbered_cs=true&include_unpublished=false'

# Exports EAD for all resources matching EADID input repository
for rlid in rlids_list:
#advanced search for EADID
	results = (requests.get(repositoryBaseURL + '/search?page=1&aq={\"query\":{\"field\":\"identifier\",\"value\":\"'+rlid+'\",\"jsonmodel_type\":\"field_query\",\"negated\":false,\"literal\":false}}', headers=headers)).json()

#Make sure the EADID input matches an EADID value in ASpace
	if results["total_hits"] is not 0:
		#get the URI of the first search result (should only be one)
		uri = results["results"][0]["id"]
		#get JSON for the resource based on above URI
		resource_json = (requests.get(baseURL + uri, headers=headers)).json()
		#get URI of Resource record
		resource_uri = resource_json["uri"]
		#replace /resources with /resource_descriptions for EAD export
		id_uri_string = resource_uri.replace("resources","resource_descriptions")
		#get user who last modified record (just print it out to the console on export confirmation)
		last_modified_by = results["results"][0]["last_modified_by"]
		#get last modified time (just print it out to console on export confirmation)
		user_mtime_full = results["results"][0]["user_mtime"]
		#remove timestamp from date - day is good enough
		user_mtime_slice = user_mtime_full[0:10]
		#get resource ID (just print out to console on export confirmation)
		resource_id = results["results"][0]["identifier"]
		aspace_id_full = results["results"][0]["id"]
		#shorten the identifier to resources/#
		aspace_id_short = aspace_id_full.replace("/repositories/2/","")
		#get the EADID value for printing
		eadID = resource_json["ead_id"]
		#set publish_status variable to check for finding aid status values
		publish_status = resource_json["finding_aid_status"]

#If the resource has a repository processing note, print it out to console. Confirm that you want to proceed with publishing
		try:
			repository_processing_note = resource_json["repository_processing_note"]
			repository_processing_note != None
			print "WARNING - Repository Processing Note: " + repository_processing_note
			input = raw_input("Proceed anyway? y/n?")
			if input == "n":
				break
			else:
				pass
		except:
			pass

#If the finding aid status is already set to publish, just export the EAD
		if "published" in publish_status:
		# Set publish to 'true' for all levels, components, notes, etc.  Same as choosing "publish all" in staff UI
			resource_publish_all = requests.post(baseURL + resource_uri + '/publish',headers=headers)
			print eadID + '--resource and all children set to published'
		#Pause for 5 seconds so publish action takes effect
			print "Pausing for 5 seconds to index publish action..."
			time.sleep(5.0)
			print "Exporting EAD file..."
			ead = requests.get(baseURL + id_uri_string + '.xml' +export_options, headers=headers).text
		# Sets the location where the files should be saved
			destination = 'C:/users/nh48/desktop/as_exports_temp/'
			f = open(destination+eadID+'.xml', 'w')
			f.write(ead.encode('utf-8'))
			f.close
			print eadID + '.xml' ' | ' + resource_id + ' | ' + aspace_id_short + ' | ' + last_modified_by + ' | ' + user_mtime_slice + ' | ' + 'exported'

#If not published, set finding aid status to published
		else:
			print "Finding aid status: " + publish_status
			resource_publish_all = requests.post(baseURL + resource_uri + '/publish',headers=headers)
			print eadID + '--resource and all children set to published'
			print "Pausing for 5 seconds to index publish action..."
			time.sleep(5.0)
			resource_json['finding_aid_status'] = 'published'
			resource_data = json.dumps(resource_json)
			#Repost the Resource with the published status
			resource_update = requests.post(baseURL + resource_uri,headers=headers,data=resource_data).json()
			print eadID + '--reposted resource with finding aid status = published'
		#Pause for 5 seconds so publish action takes effect
			print "Pausing for 5 seconds to index reposted resource..."
			time.sleep(5.0)
			print "Exporting EAD file..."
			ead = requests.get(baseURL + id_uri_string + '.xml' +export_options, headers=headers).text
		# Sets the location where the files should be saved
			destination = 'C:/users/nh48/desktop/as_exports_temp/'
			f = open(destination+eadID+'.xml', 'w')
			f.write(ead.encode('utf-8'))
			f.close
			print eadID + '.xml' ' | ' + resource_id + ' | ' + aspace_id_short + ' | ' + last_modified_by + ' | ' + user_mtime_slice + ' | ' + 'exported'
	else:
		print '***ERROR***: ' + eadid + ' does not exist!'

raw_input("Press Enter to Exit")
