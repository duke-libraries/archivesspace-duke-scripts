import requests
import json
import csv
import os
import getpass


#This script is used to batch delete archival objects using an input CSV containing a single column of archival object IDs (the ID in the URI)
#The CSV should not include a header row
#Archival object IDs can be obtained by searching in the backend SQL database, then exporting as CSV.


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
archival_objects_to_delete = raw_input("Path to input CSV: ")

#prompt for output path
deleted_archival_objects = raw_input("Path to output CSV: ")


with open(archival_objects_to_delete,'rb') as csvfile, open(deleted_archival_objects,'wb') as csvout:
    csvin = csv.reader(csvfile)
    #next(csvin, None) #ignore header row
    csvout = csv.writer(csvout)
    for row in csvin:

        #variables from the input CSV (first column is row[0])

        input_ao_id = row[0]

        #Lookup AO to make sure it exists, print something out
        try:
            archival_object_json = requests.get(aspace_url+'/repositories/'+aspace_repo+'/archival_objects/'+input_ao_id,headers=headers).json()


            #get some metadata about archival object you're going to delete and print it out
            archival_object_uri = archival_object_json['uri']
            #archival_object_title = archival_object_json['title'].encode('utf-8')
            print archival_object_uri


            archival_object_delete = requests.delete(aspace_url+'/repositories/'+aspace_repo+'/archival_objects/'+input_ao_id,headers=headers)

            print archival_object_delete

            #add status to CSV
            row.append(input_ao_id)
            row.append(archival_object_uri)
            #row.append(archival_object_title)
            row.append(archival_object_delete)

        except:
            print 'ERROR: archival object not found'
            row.append('archival object not found')

        #Write a new csv with all the info from the initial csv + the ArchivesSpace uris for the archival and archival objects
        with open(deleted_archival_objects,'ab') as csvout:
            writer = csv.writer(csvout)
            writer.writerow(row)