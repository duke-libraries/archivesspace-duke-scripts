import requests
import json
import csv
import os
import getpass
import uuid

#WARNING: USE AT YOUR OWN RISK, PROBABLY NEEDS MORE TESTING

# Starting with an input CSV, this script will use the ArchivesSpace API to batch create digital object records and link them as instances of specified archival objects. 

# This script assumes you have the Archival Object URIs already. Another script exists with similar functionality if you have only refIDs and need the API to search for the URIs.

# The script will write out a CSV containing the same information as the starting CSV plus
# the refIDs and URIs for the archival objects and the the URIs for the created digital objects.

# The 5 column input csv should include a header row and be formatted with the columns identified on line 66:
# Input CSV can be modified to supply additional input metadata for forming the archival or digital objects

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

#Prompt for archival object ID to add children to. Can locate by browsing to AO in staff interface
#archival_object_parent_id = raw_input("Archival Object Parent ID: ")


#Open Input CSV and iterate over rows
with open(archival_object_csv,'rb') as csvfile, open(updated_archival_object_csv,'wb') as csvout:
    csvin = csv.reader(csvfile)
    next(csvin, None) #ignore header row
    csvout = csv.writer(csvout)
    for row in csvin:

#INPUT CSV STUFF. This assumes you have URIs for the already created archival objects. The URI should be formatted like: #/repositories/2/archival_objects/407720

        ao_uri = row[0] 
        new_do_url = row[1]
        new_do_use_statement = row[2]
        new_do_id = row[3]
        new_do_title = row[4]

        print 'Found AO: ' + ao_uri

        # Submit a get request for the archival object and store the JSON
        archival_object_json = requests.get(aspace_url+ao_uri,headers=headers).json()

        # Add the archival object uri to the row from the csv to write it out at the end
        row.append(ao_uri)

        # If you want to reuse the display string from the archival object as the digital object title, uncomment line 86 and replace 
        # 'title':new_do_title in line 89 with 'title':display_string
        # Note: this also does not copy over any notes from the archival object
        
		#display_string = archival_object_json['display_string']		

        # Form the digital object JSON using the display string from the archival object and the identifier and the file_uri from the csv
        new_digital_object_json = {'title':new_do_title,'digital_object_id':new_do_id,'file_versions':[{'file_uri':new_do_url,'use_statement':new_do_use_statement}]}
        dig_obj_data = json.dumps(new_digital_object_json)

        # Post the digital object
        dig_obj_post = requests.post(aspace_url+'/repositories/2/digital_objects',headers=headers,data=dig_obj_data).json()

        print 'New DO: ', dig_obj_post['status']

        # Grab the digital object uri
        dig_obj_uri = dig_obj_post['uri']

        print 'New DO URI: ' + dig_obj_uri

        #publish the digital object
        if publish_true_false == 'true':
            print 'Publishing DO: ' + dig_obj_uri
            dig_obj_publish_all = requests.post(aspace_url + dig_obj_uri + '/publish',headers=headers)


        # Add the digital object uri to the row from the csv to write it out at the end
        row.append(dig_obj_uri)

        # Build a new instance to add to the archival object, linking to the digital object
        dig_obj_instance = {'instance_type':'digital_object', 'digital_object':{'ref':dig_obj_uri}}
        # Append the new instance to the existing archival object record's instances
        archival_object_json['instances'].append(dig_obj_instance)
        archival_object_data = json.dumps(archival_object_json)
        # Repost the archival object
        archival_object_update = requests.post(aspace_url+ao_uri,headers=headers,data=archival_object_data).json()

        print 'New DO added as instance of new AO: ', archival_object_update['status']

        # Write a new csv with all the info from the initial csv + the ArchivesSpace uris for the archival and digital objects
        with open(updated_archival_object_csv,'ab') as csvout:
            writer = csv.writer(csvout)
            writer.writerow(row)

        #print a new line for readability in console
        print '\n'