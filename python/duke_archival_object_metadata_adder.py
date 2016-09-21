import requests
import json
import csv
import os



#Script currently adds a repository processing note based on two column TSV input file where column 1 contains the component ref_id and column 2 contains the text of the note

# This was written under the assumption that you might have a csv (or similar), exported from ASpace or
# compiled from an ASpace exported EAD, with an existing archival object's ref_id. Using only the ref_id,
# this will use the ASpace API to search for the existing archival object, retrieve its URI, store the archival
# object's JSON, and supply a new repository_processing_note for the archival object (supplied in the input CSV),
# The script will then repost the archival object to ASpace using the update archival object endpoint

# The 2 column CSV should look like this (without a header row):
# [ASpace ref_id],[repo_processing_note]


# The archival_object_csv will be your starting TSV (as .txt) with the ASpace ref_id of the archival object's to be updated,
archival_object_csv = os.path.normpath("c:/users/nh48/desktop/ASpace_api_docs/notes_to_add.csv")

# The updated_archival_object_csv will be an updated csv that will be created at the end of this script, containing all of the same
# information as the starting csv, plus the ArchivesSpace URIs for the updated archival objects
updated_archival_object_csv = os.path.normpath("c:/users/nh48/desktop/ASpace_api_docs/notes_added.csv")

# Modify your ArchivesSpace backend url, username, and password as necessary
aspace_url = 'http://localhost:8089' #Backend URL for ASpace
username= 'admin'
password = 'admin'

#Login to ASpace backend and store the session token and some header info
auth = requests.post(aspace_url+'/users/'+username+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

#Open the CSV file and iterate through each row
with open(archival_object_csv,'rb') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:

        #Grab the text of the note you want to add from the CSV
        repo_processing_note = row[1] #column 2 in CSV, first column is column 0

        # Grab the archival object's ArchivesSpace ref_id from the CSV
        ref_id = row[0] #column 1

        print 'Ref ID: ' + ref_id

        # Use the find_by_id endpoint (only availble in v1.5+) to  use the ref_ID in the CSV to retrieve the archival object's URI
        params = {"ref_id[]":ref_id}
        lookup = requests.get(aspace_url+'/repositories/2/find_by_id/archival_objects',headers=headers, params=params).json()

        
        # Grab the archival object uri from the search results
        archival_object_uri = lookup['archival_objects'][0]['ref']

        print 'Archival Object: ' + archival_object_uri

        # Submit a get request for the archival object and store the JSON
        archival_object_json = requests.get(aspace_url+archival_object_uri,headers=headers).json()

        #print the JSON reponse to see structure and figure out where you might want to add other notes or metadata values, etc.
        #print archival_object_json

        # Continue only if the search-returned archival object's ref_id matches our starting ref_id, just to be safe
        if archival_object_json['ref_id'] == ref_id:

            # Add the archival object uri to the row from the CSV to write it out at the end
            row.append(archival_object_uri)

            # Add the new repository_processing_note to the existing archival object record
            archival_object_json['repository_processing_note'] = repo_processing_note
            archival_object_data = json.dumps(archival_object_json)

            # Repost the archival object containing the new note
            archival_object_update = requests.post(aspace_url+archival_object_uri,headers=headers,data=archival_object_data).json()

            #print confirmation that archival object was updated. Response should contain any warnings
            print 'Status: ' + archival_object_update['status']

            # Write a new CSV with all the info from the initial csv + the ArchivesSpace uris for the updated archival objects
            with open(updated_archival_object_csv,'ab') as csvout:
                writer = csv.writer(csvout)
                writer.writerow(row)
            #print a new line to the console, helps with readability
            print '\n'
