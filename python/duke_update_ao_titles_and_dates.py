import requests
import json
import csv
import os
import getpass
import ConfigParser

# Script currently updates archival object titles and dates using three column CSV input file
# Column 1 contains the AO ref_id
# Column 2 contains the updated Title
# Column 3 (optional) contains updated date expressions

# This was written under the assumption that you might have a csv (or similar), exported from ASpace or
# compiled from an ASpace exported EAD, with an existing archival object's ref_id. Using only the ref_id,
# this will use the ASpace API to search for the existing archival object, retrieve its URI, store the archival
# object's JSON, and replace the existing AO title and date expression with the new AO title and dates (supplied in the input CSV),
# The script will then repost the archival object to ASpace using the update archival object endpoint

# The 3 column CSV should look like this (without a header row):
# [AO_ref_id],[new_ao_title],[new_ao_date_expression]

# The archival_object_csv will be your starting CSC (as .txt) with the ASpace ref_id of the archival object's to be updated,
archival_object_csv = os.path.normpath("c:/users/nh48/desktop/ASpace_api_scratch/ao_updates/ao_updates.csv")

# The updated_archival_object_csv will be an updated csv that will be created at the end of this script, containing all of the same
# information as the starting csv, plus the ArchivesSpace URIs for the updated archival objects
updated_archival_object_csv = os.path.normpath("c:/users/nh48/desktop/ASpace_api_scratch/ao_updates/processed/aos_updated.csv")

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
with open(archival_object_csv,'rb') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:

        # Grab the archival object's ArchivesSpace ref_id from the CSV
        ref_id = row[0] #column 1

        #Grab the text of the note you want to add from the CSV
        new_ao_title = row[1] #column 2 in CSV

        #Grab the new date from the CSV
        new_ao_date = row[2]

        print 'Ref ID: ' + ref_id

        # Use the find_by_id endpoint (only availble in v1.5+) to  use the ref_ID in the CSV to retrieve the archival object's URI
        params = {"ref_id[]":ref_id}
        lookup = requests.get(baseURL+'/repositories/'+repository+'/find_by_id/archival_objects',headers=headers, params=params).json()

        
        # Grab the archival object uri from the search results
        archival_object_uri = lookup['archival_objects'][0]['ref']

        print 'Archival Object: ' + archival_object_uri

        # Submit a get request for the archival object and store the JSON
        archival_object_json = requests.get(baseURL+archival_object_uri,headers=headers).json()

        #print the JSON reponse to see structure and figure out where you might want to add other notes or metadata values, etc.
        #print archival_object_json

        # Continue only if the search-returned archival object's ref_id matches our starting ref_id, just to be safe. Probably not necessary...
        if archival_object_json['ref_id'] == ref_id:

            # Grab the Old AO Title and append to the CSV
            old_ao_title = archival_object_json['title']
            row.append(old_ao_title)

            # Add the archival object uri to the row from the CSV to write it out at the end
            row.append(archival_object_uri)

            # Replace the title in the existing archival object record
            archival_object_json['title'] = new_ao_title
            # Add dates to the existing archival object

            # Test if input CSV has new dates
            if new_ao_date:
                #form date expression based on dates in CSV
                new_date_json = [{"expression": new_ao_date,"date_type": "inclusive", "label": "creation", "jsonmodel_type": "date"}]
                archival_object_json['dates'] = new_date_json
            else:
                pass

            archival_object_data = json.dumps(archival_object_json)

            #print archival_object_data

            #Repost the archival object containing the new title
            archival_object_update = requests.post(baseURL+archival_object_uri,headers=headers,data=archival_object_data).json()

            #print confirmation that archival object was updated. Response should contain any warnings
            print 'Status: ' + archival_object_update['status']

            # Write a new CSV with all the info from the initial csv + the ArchivesSpace uris for the updated archival objects
            with open(updated_archival_object_csv,'ab') as csvout:
                writer = csv.writer(csvout)
                writer.writerow(row)
            #print a new line to the console, helps with readability
            print '\n'