import requests
import json
import csv
import os
import getpass
import ConfigParser

# Script currently publishes all agent records of all types and outputs log to txt file.

# local config file, contains variables
configFilePath = 'local_settings.cfg'
config = ConfigParser.ConfigParser()
config.read(configFilePath)

# URL parameters dictionary, used to manage common URL patterns
dictionary = {'baseURL': config.get('ArchivesSpace', 'baseURL'), 'repository':config.get('ArchivesSpace', 'repository'), 'user': config.get('ArchivesSpace', 'user'), 'password': config.get('ArchivesSpace', 'password')}
baseURL = '{baseURL}'.format(**dictionary)
repositoryBaseURL = '{baseURL}/repositories/{repository}/'.format(**dictionary)
repository = '{repository}'.format(**dictionary)

# authenticates the session
auth = requests.post('{baseURL}/users/{user}/login?password={password}&expiring=false'.format(**dictionary)).json()
session = auth["session"]

#if auth.status_code == 200:
print "Authenticated!"
headers = {'X-ArchivesSpace-Session':session}


#agent_corporate_ids = raw_input("List of corporate_ids:  ")
# Split comma separated list
#agent_corporate_ids_list = agent_corporate_ids.split(",")

file = open('agents_updated.txt','w')

#Get all agent corporate entity IDs
print 'Getting all agent_corporate IDs'
agent_corporate_ids = requests.get(baseURL + '/agents/corporate_entities?all_ids=true', headers=headers)
for id in sorted(agent_corporate_ids.json()):
    try:
        agent_corporate_json = requests.get(baseURL + '/agents/corporate_entities/' + str(id), headers=headers).json()
        agent_corporate_uri = agent_corporate_json['uri']
        agent_corporate_json['publish'] = True
        agent_corporate_data = json.dumps(agent_corporate_json)
        agent_corporate_update = requests.post(baseURL+agent_corporate_uri,headers=headers,data=agent_corporate_data).json()
        print agent_corporate_uri + ' ' + agent_corporate_update['status']
        file.write(agent_corporate_uri + ' ' + agent_corporate_update['status'] + '\n')
    except:
        print agent_corporate_uri + ' NOT UPDATED'
        file.write(agent_corporate_uri + 'NOT UPDATED' + '\n')
        pass


#Get all agent people IDs
print 'Getting all agent_people ids'
agent_people_ids = requests.get(baseURL + '/agents/people?all_ids=true', headers=headers)
for id in sorted(agent_people_ids.json()):
    try:
        agent_person_json = requests.get(baseURL + '/agents/people/' + str(id), headers=headers).json()
        agent_person_uri = agent_person_json['uri']
        agent_person_json['publish'] = True
        agent_person_data = json.dumps(agent_person_json)
        agent_person_update = requests.post(baseURL+agent_person_uri,headers=headers,data=agent_person_data).json()
        print agent_person_uri + ' ' + agent_person_update['status']
        file.write(agent_person_uri + ' ' + agent_person_update['status'] + '\n')
    except:
        print agent_person_uri + ' NOT UPDATED'
        file.write(agent_person_uri + 'NOT UPDATED' + '\n')
        pass

#Get all agent family IDs
print 'Getting all agent_family ids'
agent_family_ids = requests.get(baseURL + '/agents/families?all_ids=true', headers=headers)
for id in sorted(agent_family_ids.json()):
    try:
        agent_family_json = requests.get(baseURL + '/agents/families/' + str(id), headers=headers).json()
        agent_family_uri = agent_family_json['uri']
        #print 'Published? ' + str(agent_family_json['publish'])
        agent_family_json['publish'] = True
        agent_family_data = json.dumps(agent_family_json)
        agent_family_update = requests.post(baseURL+agent_family_uri,headers=headers,data=agent_family_data).json()
        print agent_family_uri + ' ' + agent_family_update['status']
        file.write(agent_family_uri + ' ' + agent_family_update['status'] + '\n')
    except:
        print agent_family_uri + ' NOT UPDATED'
        file.write(agent_family_uri + 'NOT UPDATED' + '\n')
        pass

file.close()