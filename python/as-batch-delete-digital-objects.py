import requests
import json
import csv
import os
import getpass


#This script is used to batch delete digital objects using an input CSV containing a single column of digital object IDs (the ID in the Aspace URI)
#The CSV should not have a header row


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
    #next(csvin, None) #ignore header row
    csvout = csv.writer(csvout)
    for row in csvin:

        #variables from the input CSV (first column is row[0])

        input_do_id = row[0]

        #Lookup DO to make sure it exists, print something out
        try:
            digital_object_json = requests.get(aspace_url+'/repositories/'+aspace_repo+'/digital_objects/'+input_do_id,headers=headers).json()


            #get some metadata about digital object you're going to delete and print it out
            digital_object_uri = digital_object_json['uri']
            #digital_object_title = digital_object_json['title'].encode('utf-8')
            digital_object_file_uri = digital_object_json['file_versions'][0]['file_uri']
            print digital_object_uri + " " + digital_object_file_uri

            digital_object_delete = requests.delete(aspace_url+'/repositories/'+aspace_repo+'/digital_objects/'+input_do_id,headers=headers)

            print digital_object_delete

            #add status to CSV
            row.append(input_do_id)
            row.append(digital_object_uri)
            #row.append(digital_object_title)
            row.append(digital_object_file_uri)
            row.append(digital_object_delete)

        except:
            print 'ERROR: digital object not found'
            row.append('digital object not found')

        #Write a new csv with all the info from the initial csv + the ArchivesSpace uris for the deleted digital objects
        with open(deleted_digital_objects,'ab') as csvout:
            writer = csv.writer(csvout)
            writer.writerow(row)