import requests
import json
import csv
import os
import getpass
import ConfigParser

# Script currently updates accession records, can be modified to target specific fields
# DO NOT INCLUDE HEADER ROW
# Column 1 contains the ASpace ID (from the URI)
# Column 2 contains the values to update

# The accession_updates.csv will be your starting CSV with the ASpace Accession IDs to be updated,
accession_updater_csv = os.path.normpath("c:/users/nh48/desktop/ASpace_api_scratch/accession_updates/accession_updates.csv")

# The accessions_updated.csv will be an updated csv that will be created at the end of this script, containing all of the same
# information as the starting csv, plus the ArchivesSpace URIs for the updated archival objects
accessions_updated_csv = os.path.normpath("c:/users/nh48/desktop/ASpace_api_scratch/accession_updates/processed/accessions_updated.csv")

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

#Open the CSV file and iterate through each row
with open(accession_updater_csv,'rb') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:

        # Grab the archival object's ArchivesSpace ref_id from the CSV
        accession_id = row[0] #column 1

        #Grab the value you want to update from the CSV
        updated_value = row[1] #column 2 in CSV

        #Grab the new date from the CSV
        #new_ao_date = row[2]

        #Lookup accession by URI
        #params = {"ref_id[]":ref_id}

        try:
          accession_json = requests.get(baseURL+'/repositories/'+repository+'/accessions/'+accession_id,headers=headers).json()
        #print accession_json

          accession_info = accession_json['title']

          accession_uri = accession_json['uri']

          print accession_info

        #UPDATE FIELD BELOW AS NECESSARY
          accession_json['user_defined']['enum_2'] = updated_value

          accession_data = json.dumps(accession_json)

        #Repost the archival object containing the new title
          accession_update = requests.post(baseURL+accession_uri,headers=headers,data=accession_data).json()

        #print confirmation that archival object was updated. Response should contain any warnings
          print 'Status: ' + accession_update['status']
          row.append(accession_update['status'])

          # Write a new CSV with all the info from the initial csv + the ArchivesSpace uris for the updated archival objects
         

        except:
          print 'ACCESSION NOT UPDATED'
          row.append('Accession Not Updated')
          pass

        with open(accessions_updated_csv,'ab') as csvout:
            writer = csv.writer(csvout)
            writer.writerow(row)
        #print a new line to the console, helps with readability
        print '\n'