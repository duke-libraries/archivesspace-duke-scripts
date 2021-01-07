import requests
import json
import csv
import os
import getpass

# Python 2.7
# This script creates a new digital object record in ArchivesSpace and links it as an instance to an existing archival object
# Script built to support import of DDR's ArchivesSpace Digital Object export CSV (CHANGE DISPLAY FORMAT TO USE STATEMENT VALUE IN CSV 'IMAGE-SERVICE'


#AUTHENTICATION STUFF:

#Prompt for backend URL ( e.g. http://localhost:8089) and login credentials
aspace_url = raw_input('ASpace backend URL: ')
username = raw_input('Username: ')
password = getpass.getpass(prompt='Password: ')

#Authenticate and get a session token
try:
    auth = requests.post(aspace_url+'/users/'+username+'/login?password='+password).json()
except requests.exceptions.RequestException as e:
    print "Invalid URL, try again"
    exit()
#test authentication
if auth.get("session") == None:
    print "Wrong username or password! Try Again"
    exit()
else:
#print authentication confirmation
    print "Hello " + auth["user"]["name"]

session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

#FILE INPUT / OUTPUT STUFF:
#prompt for input file path
archival_object_csv = raw_input("Path to input CSV: ")

#prompt for output path
updated_archival_object_csv = raw_input("Path to output CSV: ")

#Prompt for publishing digital objects and components (true or false)
publish_true_false = raw_input("Publish Digital Objects? true or false?: ")

#Open Input CSV and iterate over rows
with open(archival_object_csv,'rb') as csvfile, open(updated_archival_object_csv,'wb') as csvout:
    csvin = csv.reader(csvfile)
    next(csvin, None) #ignore header row
    csvout = csv.writer(csvout)
    for row in csvin:

        # Grab the archival object's ArchivesSpace ref_id from the csv
        ref_id = row[2]
        #Grab Digital Object title, identfier, and file_uri from CSV
        digital_object_title = row[7]
        digital_object_identifier = row[4]
        file_uri = row[5] #column 4 in CSV

        #Get file version use statement values from CSV (image-service, audio-streaming, etc.).
        #Be sure to supply terms from the ASpace file_version_use_statement controlled value list
        file_version_use_statement = row[6] #column 5 in CSV

        print 'Searching for ' + ref_id

        # Use the find_by_id endpoint (only availble in v1.5+) to retrieve the archival object's URI
        params = {"ref_id[]":ref_id}

        lookup = requests.get(aspace_url+'/repositories/2/find_by_id/archival_objects',headers=headers, params=params).json()

        # Grab the archival object uri from the search results. It should be the first and only result
        archival_object_uri = lookup['archival_objects'][0]['ref']

        print 'Found AO: ' + archival_object_uri

        # Submit a get request for the archival object and store the JSON
        archival_object_json = requests.get(aspace_url+archival_object_uri,headers=headers).json()

        # Continue only if the search-returned archival object's ref_id matches our starting ref_id, just to be safe
        # Note: probably no longer necessary when using the find_by_id endpoint
        if archival_object_json['ref_id'] == ref_id:

            # Add the archival object uri to the row from the csv to write it out at the end
            row.append(archival_object_uri)

            # Reuse the display string from the archival object as the digital object title
            # Note: a more sophisticated way of doing this would be to add the title and dates from the
            # archival object separately into the appropriate title and date records in the digital object
            # This also does not copy over any notes from the archival object
            #display_string = archival_object_json['display_string']

            # Form the digital object JSON using values from CSV
            dig_obj = {'title':digital_object_title,'digital_object_id':digital_object_identifier,'file_versions':[{'file_uri':file_uri,'use_statement':file_version_use_statement}]}
            dig_obj_data = json.dumps(dig_obj)

            # Post the digital object
            dig_obj_post = requests.post(aspace_url+'/repositories/2/digital_objects',headers=headers,data=dig_obj_data).json()
            #print dig_obj_post

            print 'Digital Object Status: ', dig_obj_post['status']

            # Grab the digital object uri
            dig_obj_uri = dig_obj_post['uri']

            print 'Digital Object URI: ', dig_obj_uri

            #publish the digital object
            if publish_true_false == 'true':
                print 'Publishing: ' + dig_obj_uri
                dig_obj_publish_all = requests.post(aspace_url + dig_obj_uri + '/publish',headers=headers)


            # Add the digital object uri to the row from the csv to write it out at the end
            row.append(dig_obj_uri)

            # Build a new instance to add to the archival object, linking to the digital object
            dig_obj_instance = {'instance_type':'digital_object', 'digital_object':{'ref':dig_obj_uri}}

            # Append the new instance to the existing archival object record's instances
            archival_object_json['instances'].append(dig_obj_instance)
            archival_object_data = json.dumps(archival_object_json)

            # Repost the archival object
            archival_object_update = requests.post(aspace_url+archival_object_uri,headers=headers,data=archival_object_data).json()

            print 'Archival Object Status: ' + archival_object_update['status']

            # Write a new csv with all the info from the initial csv + the ArchivesSpace uris for the archival and digital objects
            with open(updated_archival_object_csv,'ab') as csvout:
                writer = csv.writer(csvout)
                writer.writerow(row)

            #print a new line for readability in console
            print '\n'
