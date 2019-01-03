import requests
import json
import csv
import os
import getpass
import ConfigParser

# Script currently gets Agent data from ASpace as CSV

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

agent_corporate_export_csv = raw_input('Export path for Corporate Agent CSV: ')
agent_people_export_csv = raw_input('Export path for People Agents CSV: ')
agent_families_export_csv = raw_input('Export path for Family Agents CSV: ')

with open(agent_corporate_export_csv,'wb') as corpname_csvfile:
    writer = csv.writer(corpname_csvfile)
    #write CSV header row
    writer.writerow(["uri", "used_in_repo", "sort_name", "source", "rules", "sort_name_auto_generate"])

#Get all agent corporate entity IDs
    print 'Getting all agent_corporate IDs'
    agent_corporate_ids = requests.get(baseURL + '/agents/corporate_entities?all_ids=true', headers=headers)
    for id in sorted(agent_corporate_ids.json(), reverse=True):
        agent_corporate_json = requests.get(baseURL + '/agents/corporate_entities/' + str(id), headers=headers).json()
        agent_corporate_uri = agent_corporate_json['uri']
        used_in_repo = agent_corporate_json['used_within_repositories']
        agent_corporate_primary_name = agent_corporate_json['names'][0]['primary_name'].encode("utf-8")
        agent_corporate_sort_name = agent_corporate_json['names'][0]['sort_name'].encode("utf-8")
        #agent_corporate_display_name = agent_corporate_json['display_name'][0][''].encode("utf-8")
        try:
            agent_corporate_source = agent_corporate_json['names'][0]['source']
        except:
            agent_corportate_source = "NULL"
        try:
            agent_corporate_rules = agent_corporate_json['names'][0]['rules']
        except:
            agent_corporate_rules = "NULL"

        agent_corporate_sort_name_auto_generate = agent_corporate_json['names'][0]['sort_name_auto_generate']
        #agent_contact_info_json = agent_corporate_json['agent_contacts']
        print agent_corporate_uri
        row = [agent_corporate_uri, used_in_repo, agent_corporate_sort_name, agent_corporate_source, agent_corporate_rules, agent_corporate_sort_name_auto_generate]
        writer.writerow(row)

with open(agent_people_export_csv,'wb') as people_name_csvfile:
    writer = csv.writer(people_name_csvfile)
    #write CSV header row
    writer.writerow(["uri", "used_in_repo", "sort_name", "source", "rules", "sort_name_auto_generate"])

    print 'Getting all agent_people IDs'
    agent_people_ids = requests.get(baseURL + '/agents/people?all_ids=true', headers=headers)
    for id in sorted(agent_people_ids.json(), reverse=True):
        agent_people_json = requests.get(baseURL + '/agents/people/' + str(id), headers=headers).json()
        agent_people_uri = agent_people_json['uri']
        used_in_repo = agent_people_json['used_within_repositories']
        agent_people_primary_name = agent_people_json['names'][0]['primary_name'].encode("utf-8")
        agent_people_sort_name = agent_people_json['names'][0]['sort_name'].encode("utf-8")
        #agent_people_display_name = agent_people_json['display_name'][0][''].encode("utf-8")
        try:
            agent_people_source = agent_people_json['names'][0]['source']
        except:
            agent_people_source = "NULL"
        try:
            agent_people_rules = agent_people_json['names'][0]['rules']
        except:
            agent_people_rules = "NULL"

        agent_people_sort_name_auto_generate = agent_people_json['names'][0]['sort_name_auto_generate']
        #agent_contact_info_json = agent_people_json['agent_contacts']
        print agent_people_uri
        row = [agent_people_uri, used_in_repo, agent_people_sort_name, agent_people_source, agent_people_rules, agent_people_sort_name_auto_generate]
        writer.writerow(row)

with open(agent_families_export_csv,'wb') as family_name_csvfile:
    writer = csv.writer(family_name_csvfile)
    #write CSV header row
    writer.writerow(["uri", "used_in_repo", "sort_name", "source", "rules", "sort_name_auto_generate"])

    print 'Getting all agent_families IDs'
    agent_families_ids = requests.get(baseURL + '/agents/families?all_ids=true', headers=headers)
    for id in sorted(agent_families_ids.json(), reverse=True):
        agent_families_json = requests.get(baseURL + '/agents/families/' + str(id), headers=headers).json()
        agent_families_uri = agent_families_json['uri']
        used_in_repo = agent_families_json['used_within_repositories']
        agent_families_primary_name = agent_families_json['names'][0]['family_name'].encode("utf-8")
        agent_families_sort_name = agent_families_json['names'][0]['sort_name'].encode("utf-8")
        #agent_families_display_name = agent_families_json['display_name'][0][''].encode("utf-8")
        try:
            agent_families_source = agent_families_json['names'][0]['source']
        except:
            agent_families_source = "NULL"
        try:
            agent_families_rules = agent_families_json['names'][0]['rules']
        except:
            agent_families_rules = "NULL"

        agent_families_sort_name_auto_generate = agent_families_json['names'][0]['sort_name_auto_generate']
        #agent_contact_info_json = agent_families_json['agent_contacts']
        print agent_families_uri
        row = [agent_families_uri, used_in_repo, agent_families_sort_name, agent_families_source, agent_families_rules, agent_families_sort_name_auto_generate]
        writer.writerow(row)
