import requests
import json
import csv
import os
import getpass


#Script currently takes a CSV as input (with Aspace URI as first column--e.g. https://aspace.library.edu/repositories/2/archival_objects/1234) and deletes the record.
#Script also outputs separate CSV with initial data and an added column for delete status.

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
    print "Hello, you authenticated as: " + auth["user"]["name"] 

session = auth["session"]
headers = {'X-ArchivesSpace-Session':session}

repo_id = raw_input('ASpace Repo ID: ')


input_csv = raw_input('Path to input CSV: ')
output_csv = raw_input('Path to output CSV: ')

#Open the input CSV file and iterate through each row
with open(input_csv,'rb') as csvfile:
    reader = csv.reader(csvfile)
    next(csvfile, None) #ignore header row
    for row in reader:

#Get info from CSV
        record_uri = row[0]

        print 'Looking up record: ' + record_uri
        try:
            record_json = requests.get(aspace_url+record_uri,headers=headers).json()

            print 'Found ' + record_json['uri']

            record_update = requests.delete(aspace_url+record_uri,headers=headers).json()
            print 'Status: ' + record_update['status']
#print confirmation that record was deleted. Response should contain any warnings
            row.append(record_update['status'])
        except:
            print 'error on record: ' + record_uri
            row.append('ERROR- not processed')

        with open(output_csv,'ab') as csvout:
            writer = csv.writer(csvout)
            writer.writerow(row)
        #print a new line to the console, helps with readability
        print '\n'
print "All done"
