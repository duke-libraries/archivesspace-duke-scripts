import requests
import json
import csv
import os
import getpass


#Add OPTION TO PUBLISH FILE VERSIONS?

#This script is used to batch update metadata for digital objects in ASpace using CSV input


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

#FILE INPUT / OUTPUT STUFF:
#prompt for input file path
digital_objects_input_csv = raw_input("Path to input CSV: ")

#prompt for output path
updated_digital_objects_csv = raw_input("Path to output CSV: ")


with open(digital_objects_input_csv,'rb') as csvfile, open(updated_digital_objects_csv,'wb') as csvout:
    csvin = csv.reader(csvfile)
    next(csvin, None) #ignore header row
    csvout = csv.writer(csvout)
    for row in csvin:

        #variables from the input CSV (first column is row[0])
        
        input_do_uri = row[0]
        input_do_identifier = row[1]
        input_do_title = row[2]
        input_do_publish = row[3]
        input_linked_instance = row[4]
        input_file_version_uri_1 = row[5]
        input_use_statement_1 = row[6]
        input_file_version_uri_2 = row[7]
        input_use_statement_2 = row[8]
        
        # Use input DO URI to submit a get request for the digital object and store the JSON
        digital_object_json = requests.get(aspace_url+input_do_uri,headers=headers).json()

        #Overwrite existing fields with new values from CSV. Comment out any fields you don't want to overwrite
        digital_object_json['digital_object_id'] = input_do_identifier
        digital_object_json['title'] = input_do_title
        digital_object_json['file_versions'][0]['file_uri'] = input_file_version_uri_1
        digital_object_json['file_versions'][0]['use_statement'] = input_use_statement_1
        #digital_object_json['file_versions'][1]['file_uri'] = input_file_version_uri_2
        #digital_object_json['file_versions'][1]['use_statement'] = input_use_statement_2

        #Form the JSON for the updated digital object
        digital_object_data = json.dumps(digital_object_json)

        #Repost the updated digital object
        digital_object_update = requests.post(aspace_url+input_do_uri,headers=headers,data=digital_object_data).json()
        #Capture status response of post request
        update_status = digital_object_update['status']

        #Print confirmation that archival object was updated. Response should contain any warnings
        print digital_object_json['uri'] + ': ' + update_status

        #add update status to CSV
        row.append(update_status)

        #Lookup the digital object again and capture JSON response for updated digital object
        updated_digital_object_json = requests.get(aspace_url+input_do_uri,headers=headers).json()

        #Just stuff all the JSON for the updated object in a cell at the end of the CSV...probably a bad idea
        row.append(updated_digital_object_json)

        #Write a new csv with all the info from the initial csv + the ArchivesSpace uris for the archival and digital objects
        with open(updated_digital_objects_csv,'ab') as csvout:
            writer = csv.writer(csvout)
            writer.writerow(row)