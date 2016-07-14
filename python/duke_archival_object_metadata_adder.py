import requests
import json
import csv
import os


#This Script Works. --Noah
#Currently adds a repository processing note based on two column TSV input file where column 1 contains the component ref_id and column 2 contains the text of the note


# This was written under the assumption that you might have a csv (or similar), exported from ASpace or
# compiled from an ASpace exported EAD, with an existing archival object's ref_id. Using only the ref_id,
# this will use the ASpace API to search for the existing archival object, retrieve its URI, store the archival
# object's JSON, and supply a new repository_processing_note for the archival object (supplied in the input TSV),
# The script will then repost the archival object to ASpace using the update archival object endpoint

# The 2 column TSV will look like this:
# [Aspace ref_id]	[repo_processing_note]


# The archival_object_csv will be your starting TSV (as .txt) with the ASpace ref_id of the archival object's to be updated,
archival_object_csv = os.path.normpath("c:/users/nh48/desktop/gedney_sample_repo_note_updater_spreadsheet.txt")

# The updated_archival_object_csv will be an updated csv that will be created at the end of this script, containing all of the same
# information as the starting csv, plus the ArchivesSpace uris for the archival and digital objects
updated_archival_object_csv = os.path.normpath("c:/users/nh48/desktop/gedney_archival_objects_updated.csv")

# Modify your ArchivesSpace backend url, username, and password as necessary
aspace_url = 'http://localhost:8089' #Backend URL for ASpace
username= 'admin'
password = 'admin'

auth = requests.post(aspace_url+'/users/'+username+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

#Modified for TSV input, which is default output of aspace_dig_guide_creator.xsl
with open(archival_object_csv,'rb') as tsvin, open(updated_archival_object_csv,'wb') as csvout:
    tsvin = csv.reader(tsvin, delimiter='\t')
    next(tsvin, None) #ignore header row
    csvout = csv.writer(csvout)
    for row in tsvin:

#Original code below assumes CSV input format
#with open(archival_object_csv,'rb') as csvfile:
#    reader = csv.reader(csvfile)
#    next(reader, None)
#    for row in reader:

        # Use an identifier and a file_uri from the csv to create the digital object
        # If you don't have specific identifiers and just want a random string,
        # you could import uuid up top and do something like 'identifier = uuid.uuid4()'
        repo_processing_note = row[1] #column 2 in CSV, first column is column 0

        # Grab the archival object's ArchivesSpace ref_id from the csv
        ref_id = row[0] #column 1

        print ref_id

        # Search ASpace for the ref_id
        search = requests.get(aspace_url+'/repositories/2/search?page=1&q='+ref_id,headers=headers).json() #change repository number as needed

        
        # Grab the archival object uri from the search results
        archival_object_uri = search['results'][0]['uri']

        print archival_object_uri

        # Submit a get request for the archival object and store the JSON
        archival_object_json = requests.get(aspace_url+archival_object_uri,headers=headers).json()

        #print the JSON reponse to see where you might want to add other notes or metadata values, etc.
        #print archival_object_json

        # Continue only if the search-returned archival object's ref_id matches our starting ref_id, just to be safe
        if archival_object_json['ref_id'] == ref_id:

            # Add the archival object uri to the row from the csv to write it out at the end
            row.append(archival_object_uri)

            # Add the new repository_processing_note to the existing archival object record
            archival_object_json['repository_processing_note'] = repo_processing_note
            archival_object_data = json.dumps(archival_object_json)

            # Repost the archival object containing the new note
            archival_object_update = requests.post(aspace_url+archival_object_uri,headers=headers,data=archival_object_data).json()

            #print confirmation that archival object was updated. response should contain any warnings
            print archival_object_update

            # Write a new csv with all the info from the initial csv + the ArchivesSpace uris for the updated archival objects
            with open(updated_archival_object_csv,'ab') as csvout:
                writer = csv.writer(csvout)
                writer.writerow(row)