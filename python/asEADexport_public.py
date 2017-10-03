#!/usr/bin/env python

import requests
import json

# the base URL of your ArchivesSpace installation
baseURL = '[backend-url]'
# the id of your repository
repository = '2'
# the username to authenticate with
user = '[username]'
# the password for the username above
password = '[password]'

# authenticates the session
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
#if auth.status_code == 200:
	#print "Authenticated!"
headers = {'X-ArchivesSpace-Session':session}

#number components and include DAOs
export_options = '?numbered_cs=true&include_daos=true&include_unpublished=false'

# Gets the IDs of all resources in the repository
resourceIds = requests.get(baseURL + '/repositories/'+repository+'/resources?all_ids=true', headers=headers)

# Exports EAD for all resources in repositories/2 where finding_aid_status = "published"
for id in resourceIds.json():
	resource = (requests.get(baseURL + '/repositories/'+repository+'/resources/' + str(id), headers=headers)).json()
	resourceID = resource["id_0"]
	eadID = resource["ead_id"]
	published = resource["finding_aid_status"]
	if "published" in published:
		ead = requests.get(baseURL + '/repositories/'+repository+'/resource_descriptions/'+str(id)+'.xml'+export_options, headers=headers).text
		# Sets the location where the files should be saved
		destination = '[filepath to save xml files]'
		f = open(destination+eadID+'.xml', 'w')
		f.write(ead.encode('utf-8'))
		f.close
		
		print eadID + ' exported to ' + destination