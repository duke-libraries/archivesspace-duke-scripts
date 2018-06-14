import requests
import json
import csv
import os
import getpass
import datetime


#This script is used to batch delete digital objects based on CSV input where column 1 contains Digital Object Identifiers.
#Digital object IDs can be obtained from the repository (typically ARKs) or by searching in the AS backend SQL database and exporting records as CSV
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

#    print 'Processing delete batch...'

    for row in csvin:

        #variables from the input CSV (first column is row[0])

        input_do_ark_identifier = row[0]

        print 'Looking up: '+ input_do_ark_identifier

        try:

            #Lookup DO to make sure it exists, print something out
            #Use the find_by_id endpoint (only available in v1.5+) to retrieve the digital object's URI
            params = {"digital_object_id[]":input_do_ark_identifier}
            lookup = requests.get(aspace_url+'/repositories/2/find_by_id/digital_objects',headers=headers, params=params).json()

            #Grab the digital object uri from the search results. It should be the first and only result...I think
            digital_object_uri = lookup['digital_objects'][0]['ref']

            print 'Found: ' + digital_object_uri

            digital_object_delete = requests.delete(aspace_url+digital_object_uri,headers=headers).json()

            print 'Status: ' + digital_object_delete['status']

            #add URI and delete status to CSV
            row.append(digital_object_uri)
            row.append(digital_object_delete['status'])
            row.append(datetime.datetime.now().isoformat())

        except:
            print 'STATUS: OBJECT NOT FOUND: ' + input_do_ark_identifier
            row.append('ERROR: OBJECT NOT FOUND')
            row.append('ERROR')
            row.append(datetime.datetime.now().isoformat())

        #Write a new csv with all the info from the initial csv + the ArchivesSpace URIs and delete status for digital objects
        with open(deleted_digital_objects,'ab') as csvout:
            writer = csv.writer(csvout)
            writer.writerow(row)
print 'ALL DONE!'