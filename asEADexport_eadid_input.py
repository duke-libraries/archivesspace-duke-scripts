#!/usr/bin/env python

import sys
import requests
import json
import re
import ConfigParser

#resources = raw_input("List of resourceIDs:  ")
#resources_list = resources.split(",")

# local config file, contains variables
configFilePath = 'local_settings.cfg'
config = ConfigParser.ConfigParser()
config.read(configFilePath)

# URL parameters dictionary, used to manage common URL patterns
dictionary = {'baseURL': config.get('ArchivesSpace', 'baseURL'), 'repository':config.get('ArchivesSpace', 'repository'), 'user': config.get('ArchivesSpace', 'user'), 'password': config.get('ArchivesSpace', 'password')}
baseURL = '{baseURL}'.format(**dictionary)
repositoryBaseURL = '{baseURL}/repositories/{repository}/'.format(**dictionary)

# Prompt for input
eadids = raw_input("list of EADIDs:  ")
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
	print id_uri_string
	eadID = resource["ead_id"]
	published = resource["finding_aid_status"]
	if "published" in published:
		ead = requests.get(baseURL + id_uri_string + '.xml' +export_options, headers=headers).text
		# Sets the location where the files should be saved
		destination = 'C:/users/nh48/desktop/as_exports_temp/'
		f = open(destination+eadID+'.xml', 'w')
		f.write(ead.encode('utf-8'))
		f.close
		
		print eadID + '.xml' + ' exported to ' + destination
	if not "published" in published:
		print eadID + ' is not marked as published'