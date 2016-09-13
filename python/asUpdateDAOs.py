import requests
import json
import csv
import os

#USE AT YOUR OWN RISK - NEEDS MORE TESTING!!!

#This script is used to update Digital Object file version URIs in ASpace based on an input CSV containing refIDs of the linked Archival Object
#The 5 column CSV should look like this (without column headers):
#[old file version use statement],[old file version URI],[new file version URI],[ASpace ref_id],[ark identifier in DDR (e.g. ark:/87924/r34j0b091)]

#Path to input CSV file
archival_object_csv = 'C:/Users/nh48/desktop/ASpace_api_docs/wia_update_daos.csv'

#The script will output another CSV file containing all of the same information as the starting csv, plus the ArchivesSpace uris for the updated archival objects and and digital objects
#Path to output CSV
updated_archival_object_csv = 'C:/Users/nh48/desktop/updated_daos.csv'

#Modify the ArchivesSpace backend url, username, and password as necessary
aspace_url = 'http://localhost:8089'
username= 'admin'
password = 'admin'

auth = requests.post(aspace_url+'/users/'+username+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

with open(archival_object_csv,'rb') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:

        #variables from the input CSV (first column is row[0])
        ark_identifier = row[4]
        old_file_version_uri_spreadsheet = row[1]
        old_file_version_use_statement_spreadsheet = row[0]
        file_version_uri = row[2]

        #Grab the archival object's ArchivesSpace ref_id from the csv
        ref_id = row[3]

        print 'Ref ID ' + ref_id

        # Use the find_by_id endpoint (only availble in v1.5+) to retrieve the archival object's URI
        params = {"ref_id[]":ref_id}
        lookup = requests.get(aspace_url+'/repositories/2/find_by_id/archival_objects',headers=headers, params=params).json()

        # Grab the archival object uri from the search results. It should be the first and only result
        archival_object_uri = lookup['archival_objects'][0]['ref']

        print 'AO URI ' + archival_object_uri

        # Submit a get request for the archival object and store the JSON
        archival_object_json = requests.get(aspace_url+archival_object_uri,headers=headers).json()

        # Continue only if the search-returned archival object's ref_id matches our starting ref_id, just to be safe
        # Note: probably no longer necessary when using the find_by_id endpoint
        if archival_object_json['ref_id'] == ref_id:

            #for each archival object, find only the instances where instance_type = 'digital_object'
            for instances in archival_object_json['instances']:
                if instances['instance_type'] == 'digital_object':
                    digital_object_uri = instances['digital_object']['ref'] #returns something like /repositories/2/digital_objects/7230
                    digital_object_json = requests.get(aspace_url+digital_object_uri,headers=headers).json()
                    #For each digital object, update only the file version where the file_uri matches the old_file_version_uri_spreadsheet (from input spreadsheet)
                    file_version_json = digital_object_json['file_versions']
                    #Get the index (position) of the file version that you want to update (the one where the file URI matches your input file URI in the spreadsheet)
                    file_version_index = next((index for (index, d) in enumerate(file_version_json) if d["file_uri"] == old_file_version_uri_spreadsheet), None)
                    #print that index for confirmation, should return 'None' if no match
                    print file_version_index
                    #iterate over file versions and make sure that the file_uri and use_statement match your input
                    for file_versions in digital_object_json['file_versions']:
                        if file_versions['file_uri'] == old_file_version_uri_spreadsheet and file_versions['use_statement'] == old_file_version_use_statement_spreadsheet:

                            print 'Mathing file version found'

                            #Overwrite the file uri for only the file version you matched above.  Use the index position of the matched file version to update the correct one.  This is probably terrible logic...
                            digital_object_json['file_versions'][file_version_index]['file_uri'] = file_version_uri
                            #Add the ARK ID from the input spreadsheet as the Digital Object Identifier (will overwrite any existing ID)
                            digital_object_json['digital_object_id'] = ark_identifier
                            #Form the JSON to post updates
                            digital_object_data = json.dumps(digital_object_json)

                            # Repost the digital object with the updated file version URI and digital objectID
                            digital_object_update = requests.post(aspace_url+digital_object_uri,headers=headers,data=digital_object_data).json()

                            #print confirmation that archival object was updated. response should contain any warnings
                            print 'Digital Object Status:', digital_object_update['status']
                            #Add the archival object uri and digital object uri to the row from the csv to write it out at the end
                            row.append(archival_object_uri)
                            row.append(digital_object_uri)

                        else:
                            print 'File version does not match'

#Write a new csv with all the info from the initial csv + the ArchivesSpace uris for the archival and digital objects
        with open(updated_archival_object_csv,'ab') as csvout:
             writer = csv.writer(csvout)
             writer.writerow(row)
        print '\n'
