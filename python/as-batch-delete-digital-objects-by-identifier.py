import requests
import json
import csv
import os
import getpass


#This script is used to batch delete digital objects based on CSV input of Digital Object Identifiers.
#The first column in the CSV should hold the Digital Object Identifier (an ARK, handle, etc.)
#Digital object IDs can be obtained by searching in the backend SQL database and exporting records as CSV
#Uses find_by_id/digital_objects endpoint. Only available in 2.1?


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
digital_objects_to_delete = raw_input("Path to input CSV: ")

#prompt for output path
deleted_digital_objects = raw_input("Path to output CSV: ")


with open(digital_objects_to_delete,'rb') as csvfile, open(deleted_digital_objects,'wb') as csvout:
    csvin = csv.reader(csvfile)
    next(csvin, None) #ignore header row
    csvout = csv.writer(csvout)
    for row in csvin:

        #variables from the input CSV (first column is row[0])

        input_do_ark_identifier = row[0]

        print input_do_ark_identifier

        #Lookup DO to make sure it exists, print something out
        # Use the find_by_id endpoint (only availble in v1.5+) to retrieve the archival object's URI
        params = {"digital_object_id[]":input_do_ark_identifier}
        digital_object_json = requests.get(aspace_url+'/repositories/2/find_by_id/digital_objects',headers=headers, params=params).json()

        #get some metadata about digital object you're going to delete and print it out
        digital_object_uri = digital_object_json['uri']
        #digital_object_title = digital_object_json['title'].encode('utf-8')
        digital_object_file_uri = digital_object_json['file_versions'][0]['file_uri']
        print digital_object_uri + digital_object_file_uri

        digital_object_delete = requests.delete(aspace_url+digital_object_uri,headers=headers)

        print digital_object_delete

        #add status to CSV
        row.append(input_do_ark_identifier)
        row.append(digital_object_uri)
        #row.append(digital_object_title)
        row.append(digital_object_file_uri)
        row.append(digital_object_delete)

        #Write a new csv with all the info from the initial csv + the ArchivesSpace uris for the archival and digital objects
        with open(deleted_digital_objects,'ab') as csvout:
            writer = csv.writer(csvout)
            writer.writerow(row)