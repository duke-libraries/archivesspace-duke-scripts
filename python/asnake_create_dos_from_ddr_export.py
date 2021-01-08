import csv
import configparser
from asnake.client import ASnakeClient
from asnake.aspace import ASpace

# Python 3 and ASnake
# This script takes as input a CSV exported from DDR and then creates a new digital object record in ArchivesSpace for each row and links it as an instance to an existing archival object
# Script built to support import of DDR's ArchivesSpace Digital Object export CSV
# Modify values in the display_format column to align with file_version_use_statement values in ASpace (e.g. 'image-service', 'audio-streaming', 'video-streaming', etc.)

#ASpace credentials and other variables stored in local config file in same directory as script
configFilePath = 'asnake_local_settings.cfg'
config = configparser.ConfigParser()
config.read(configFilePath)

#Read variables from asnake_local_settings.cfg
AS_username = config.get('ArchivesSpace','user')
AS_password = config.get('ArchivesSpace','password')
AS_api_url = config.get('ArchivesSpace','baseURL')

AS_repository_id = config.get('ArchivesSpace','repository')


#Log Into ASpace
aspace = ASpace(baseurl=AS_api_url,
                username=AS_username,
                password=AS_password)

aspace_client = ASnakeClient(baseurl=AS_api_url,
                             username=AS_username,
                             password=AS_password)
aspace_client.authorize()

#Prompt for paths to input CSV and output CSV
input_csv = input("Path to DDR export CSV:  ")
output_csv = input("Path to report CSV: ")

#Prompt for publish true/false
publish_true_false = input("Publish Digital Objects? true or false?: ")

#Open Input CSV and iterate over rows
with open(input_csv,'rt', newline='') as csvfile, open(output_csv,'wt', newline='') as csvout:
    csvin = csv.reader(csvfile)
    next(csvin, None) #ignore header row
    csvout = csv.writer(csvout)
    
    for row in csvin:
        #Get the AO ref_id from the input csv
        ref_id = row[2]
        #Get DO title, identfier, and file_uri from CSV
        digital_object_title = row[7]
        digital_object_identifier = row[4]
        file_uri = row[5] #column 4 in CSV

        #Get file_version_use_statement values from input CSV (image-service, audio-streaming, etc.).
        #Be sure to supply terms from the ASpace file_version_use_statement controlled value list
        file_version_use_statement = row[6] #column 5 in CSV

        print ('Searching for ' + ref_id)

        # Use the find_by_id endpoint (only availble in v1.5+) to retrieve the archival object's URI
        params = {"ref_id[]":ref_id}
        lookup = aspace_client.get('/repositories/2/find_by_id/archival_objects', params=params).json()
        
        # Grab the archival object uri from the search results. It should be the first and only result
        archival_object_uri = lookup['archival_objects'][0]['ref']

        print ('Found AO: ' + archival_object_uri)

        #Get AO and store the JSON
        archival_object_json = aspace_client.get(archival_object_uri).json()

        # Continue only if the search-returned AO's ref_id matches our starting ref_id, just to be safe
        # Note: probably no longer necessary when using the find_by_id endpoint
        if archival_object_json['ref_id'] == ref_id:

            # Add the AO uri to the row from the csv to write it out at the end
            row.append(archival_object_uri)

            # Form the DO JSON using values from CSV
            dig_obj = {'title':digital_object_title,
                       'digital_object_id':digital_object_identifier,
                       'file_versions':[{'file_uri':file_uri,
                                         'use_statement':file_version_use_statement
                                         }]
                       }

            # Post the DO
            dig_obj_post = aspace_client.post('/repositories/2/digital_objects',json=dig_obj).json()

            print ('Digital Object Status: ', dig_obj_post['status'])

            # Grab the URI of the posted DO
            dig_obj_uri = dig_obj_post['uri']

            print ('Digital Object URI: ', dig_obj_uri)

            #publish the DO
            if publish_true_false == 'true':
                print ('Publishing: ' + dig_obj_uri)
                dig_obj_publish_all = aspace_client.post(dig_obj_uri + '/publish')

            # Add the DO uri to the row from the csv to write it out at the end
            row.append(dig_obj_uri)

            # Build a new instance to add to the AO, linking to the digital object
            dig_obj_instance = {'instance_type':'digital_object', 
                                'digital_object':{'ref':dig_obj_uri}
                                }

            # Append the new instance to the existing archival object record's instances
            archival_object_json['instances'].append(dig_obj_instance)

            # Repost the archival object
            archival_object_update = aspace_client.post(archival_object_uri, json=archival_object_json).json()

            print ('Archival Object Status: ' + archival_object_update['status'])

            # Write a new csv with all the info from the initial csv + the ArchivesSpace uris for the archival and digital objects
            with open(output_csv,'at', newline='') as csvout:
                writer = csv.writer(csvout)
                writer.writerow(row)

            #print a new line for readability in console
            print ('\n')