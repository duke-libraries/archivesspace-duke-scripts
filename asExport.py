#!/usr/bin/env python

import requests
import json

# the base URL of your ArchivesSpace installation
baseURL = 'http://webapp-dev-01.lib.duke.edu:9089'
# the id of your repository
repository = '11'
# the username to authenticate with
user = 'admin'
# the password for the username above
password = 'admin'

# authenticates the session
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
#if auth.status_code == 200:
	#print "Authenticated!"
headers = {'X-ArchivesSpace-Session':session}

#number components and include DAOs
export_options = '?numbered_cs=true&?include_daos=true'

# Gets the IDs of all resources in the repository
resourceIds = requests.get(baseURL + '/repositories/'+repository+'/resources?all_ids=true', headers=headers)

# Exports EAD for all resources whose IDs contain 'RL'
for id in resourceIds.json():
	resource = (requests.get(baseURL + '/repositories/'+repository+'/resources/' + str(id), headers=headers)).json()
	resourceID = resource["id_0"]
	eadID = resource["ead_id"]
	if "RL" in resourceID:
		ead = requests.get(baseURL + '/repositories/'+repository+'/resource_descriptions/'+str(id)+'.xml'+export_options, headers=headers).text
		# Sets the location where the files should be saved
		destination = 'C:/users/nh48/desktop/EAD_python_export/'
		f = open(destination+eadID+'.xml', 'w')
		f.write(ead.encode('utf-8'))
		f.close
		print eadID + ' exported to ' + destination