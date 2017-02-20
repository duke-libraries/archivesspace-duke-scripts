import requests
import json
import csv
import os
import getpass

#This script is used to export metadata for digital objects from ASpace as CSV

#Path to output CSV
digital_object_export_csv = 'C:/Users/nh48/desktop/digital_objects_in_aspace.csv'

#Prompt for authentication
aspace_url = raw_input('Aspace backend URL: ')
aspace_repo = raw_input('Repo number: ')
username= raw_input('Username: ')
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

digital_objects_list = requests.get(aspace_url+ '/repositories/' + aspace_repo + '/digital_objects?all_ids=true',headers=headers).json()

with open(digital_object_export_csv,'wb') as csvfile:
    writer = csv.writer(csvfile)
    #write CSV header row
    writer.writerow(["digital_object_URI", "digital_object_identifier", "digital_object_title", "digital_object_publish", "file_version_uri", "file_version_use_statement", "linked_instances"])

    for digital_object_id in digital_objects_list:
        do_json = requests.get(aspace_url+'/repositories/2/digital_objects/' + str(digital_object_id),headers=headers).json()

        digital_object_URI = do_json['uri']
        digital_object_identifier = do_json['digital_object_id']
        digital_object_title = do_json['title']
        digital_object_publish = do_json['publish']

        try:
            file_version_uri = do_json['file_versions'][0]['file_uri']
        except:
            pass

        try:
            file_version_use_statement = do_json['file_versions'][0]['use_statement']
        except:
            pass

        try:
            linked_instances = do_json['linked_instances'][0]['ref']
        except:
            pass

        #write data to CSV
        row = [digital_object_URI, digital_object_title.encode("utf-8"), digital_object_publish, file_version_uri.encode("utf-8"), file_version_use_statement, linked_instances]
        writer.writerow(row)
        print 'Exporting: ' + file_version_uri.encode("utf-8")