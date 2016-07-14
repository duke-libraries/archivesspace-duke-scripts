#!/usr/bin/env python

import sys
import requests
import json
import re
import ConfigParser


# local config file, contains variables
configFilePath = 'local_settings.cfg'
config = ConfigParser.ConfigParser()
config.read(configFilePath)

# URL parameters dictionary, used to manage common URL patterns
dictionary = {'baseURL': config.get('ArchivesSpace', 'baseURL'), 'repository':config.get('ArchivesSpace', 'repository'), 'user': config.get('ArchivesSpace', 'user'), 'password': config.get('ArchivesSpace', 'password')}
baseURL = '{baseURL}'.format(**dictionary)
repositoryBaseURL = '{baseURL}/repositories/{repository}/'.format(**dictionary)

# Prompt for input, a comma separated list of EADID values (e.g. johndoepapers, janedoepapers, johnandjanedoepapers)
eadids = raw_input("List of EADIDs:  ")
# Split comma separated list
eadids_list = eadids.split(",")

# authenticates the session
auth = requests.post('{baseURL}/users/{user}/login?password={password}&expiring=false'.format(**dictionary)).json()
session = auth["session"]

#if auth.status_code == 200:
print "Authenticated!"
headers = {'X-ArchivesSpace-Session':session}

#number components and include DAOs
export_options = '?numbered_cs=true&?include_daos=true&?include_unpublished=false'


# Exports EAD for all resources in repositories/2 where finding_aid_status = "published"
for eadid in eadids_list:
	
	results = (requests.get(repositoryBaseURL + '/search?page=1&aq={\"query\":{\"field\":\"ead_id\",\"value\":\"'+eadid+'\",\"jsonmodel_type\":\"field_query\",\"negated\":false,\"literal\":false}}', headers=headers)).json()
	
#	print results


	if results["total_hits"] is not 0:
		#print (json.dumps(results, indent=2))
		#resource = (requests.get(baseURL + '/repositories/'+repository+'/resources/' + str(id), headers=headers)).json()
		#take the URI of the first search result
		uri = results["results"][0]["id"]
		#print 'URI:  ' + uri
		#get JSON for the resource based on above URI
		resource = (requests.get(baseURL + uri, headers=headers)).json()
		#print (json.dumps(resource, indent=2))
		id = resource["uri"]
		id_uri_string = id.replace("resources","resource_descriptions")
		last_modified_by = results["results"][0]["last_modified_by"]
		user_mtime_full = results["results"][0]["user_mtime"]
		#remove timestamp from date
		user_mtime_slice = user_mtime_full[0:10]
		resource_id = results["results"][0]["identifier"]
		aspace_id_full = results["results"][0]["id"]
		#shorten the identifier to resources/#
		aspace_id_short = aspace_id_full.replace("/repositories/2/","")
		#print 'Exporting' + eadid + ': ' +id_uri_string
		eadID = resource["ead_id"]
		publish_status = resource["finding_aid_status"]
		if "published" in publish_status:
			ead = requests.get(baseURL + id_uri_string + '.xml' +export_options, headers=headers).text
		# Sets the location where the files should be saved
			destination = 'C:/users/nh48/desktop/as_exports_temp/'
			f = open(destination+eadID+'.xml', 'w')
			f.write(ead.encode('utf-8'))
			f.close
			print eadID + '.xml' ' | ' + resource_id + ' | ' + aspace_id_short + ' | ' + last_modified_by + ' | ' + user_mtime_slice + ' | ' + 'exported'
		else:
			
			print '***ERROR***: ' + eadID + ' is marked ' + publish_status + ' not "published"'
	else:
		print '***ERROR***: ' + eadid + ' does not exist!'