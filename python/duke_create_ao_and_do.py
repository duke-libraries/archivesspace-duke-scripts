import requests
import json
import csv
import os
import getpass
import uuid

#WARNING: USE AT YOUR OWN RISK, PROBABLY NEEDS MORE TESTING

# Starting with an input CSV, this script will use the ArchivesSpace API to batch create archival object records in ASpace 
# as children of a specified archival object parent (e.g. a series/subseries/file).
# The script will then create digital object records and link them as instances of the newly created archival objects

# Finally, the script will write out a CSV containing the same information as the starting CSV plus
# the refIDs and URIs for the created archival objects and the the URIs for the created digital objects

# The 9 column input csv should include a header row and be formatted with the columns identified on line 72:
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

#Propt for archival object ID to add children to. Can locate by browsing to AO in staff interface
archival_object_parent_id = raw_input("Archival Object Parent ID: ")


#Open Input CSV and iterate over rows
with open(archival_object_csv,'rb') as csvfile, open(updated_archival_object_csv,'wb') as csvout:
    csvin = csv.reader(csvfile)
    next(csvin, None) #ignore header row
    csvout = csv.writer(csvout)
    for row in csvin:

#ARCHIVAL OBJECT STUFF

        #Create a unique refID for archival object before import
        uid = uuid.uuid1()
        ref_id = str(uid)
        # Use metadata from CSV to create archival object children of existing archival object
        new_ao_level = row[0]
        new_ao_title = row[1]
        new_ao_dates = row[2] # currently nothing happens with this
        new_ao_extent = row[3] # currently nothing happens with this
        new_ao_container_1_number = row[4]
        new_ao_container_2_type = row[5]
        new_ao_container_2_number = row[6] # also digial object identifier?
        new_do_url = row[7]
        new_do_use_statement = row[8]

        #Form the new Archival Object JSON
        new_ao_json = {'children': [{'ref_id': ref_id,'title': new_ao_title,'published': 'true', 'level': new_ao_level,'instances': [{'instance_type':'mixed_materials','container':{'type_1':'box','indicator_1':new_ao_container_1_number,'type_2':new_ao_container_2_type,'indicator_2':new_ao_container_2_number}}]}]}
        new_ao_data = json.dumps(new_ao_json)

        #post archival object as child of specified parent using /children endpoint
        new_ao_post = requests.post(aspace_url+'/repositories/2/archival_objects/' + archival_object_parent_id + '/children',headers=headers,data=new_ao_data).json()
        print 'Created new AO child of: ', new_ao_post['id']


 ##DIGITAL OBJECT STUFF
        # Use the find_by_id endpoint (only availble in v1.5+) to retrieve the archival object's URI
        params = {"ref_id[]":ref_id}
        lookup = requests.get(aspace_url+'/repositories/2/find_by_id/archival_objects',headers=headers, params=params).json()

        # Grab the archival object uri from the search results. It should be the first and only result
        archival_object_uri = lookup['archival_objects'][0]['ref']

        print 'Found new AO: ' + archival_object_uri

        # Submit a get request for the archival object and store the JSON
        archival_object_json = requests.get(aspace_url+archival_object_uri,headers=headers).json()

        # Continue only if the search-returned archival object's ref_id matches our starting ref_id, just to be safe
        # Note: probably no longer necessary when using the find_by_id endpoint
        if archival_object_json['ref_id'] == ref_id:

            # Add the archival object uri to the row from the csv to write it out at the end
            row.append(archival_object_uri)
            row.append(ref_id)
            # Reuse the display string from the archival object as the digital object title
            # Note: a more sophisticated way of doing this would be to add the title and dates from the
            # archival object separately into the appropriate title and date records in the digital object
            # This also does not copy over any notes from the archival object
            display_string = archival_object_json['display_string']

            # Form the digital object JSON using the display string from the archival object and the identifier and the file_uri from the csv
            new_digital_object_json = {'title':new_ao_title,'digital_object_id':new_ao_container_2_number,'file_versions':[{'file_uri':new_do_url,'use_statement':new_do_use_statement}]}
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
            archival_object_update = requests.post(aspace_url+archival_object_uri,headers=headers,data=archival_object_data).json()

            print 'New DO added as instance of new AO: ', archival_object_update['status']

            # Write a new csv with all the info from the initial csv + the ArchivesSpace uris for the archival and digital objects
            with open(updated_archival_object_csv,'ab') as csvout:
                writer = csv.writer(csvout)
                writer.writerow(row)

            #print a new line for readability in console
            print '\n'
