import requests
import json
import csv
import os
import getpass


#Script currently takes a two-column CSV as input (AO ID, desired level value) and updates level attribute accordingly.

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
    #next(csvfile, None) #ignore header row
    for row in reader:

#Get info from CSV
        ao_id = row[0]
        desired_level = row[1]

        print 'Looking up Archival Object: ' + ao_id
        try:
            ao_json = requests.get(aspace_url+'/repositories/'+repo_id+'/archival_objects/'+ao_id,headers=headers).json()

            # Grab the archival object uri from the search results. It should be the first and only result
            ao_uri = ao_json['uri']
            ao_title = ao_json['title']

            print 'Found ' + ao_uri

            #Change level value based on column 2 in CSV input
            ao_json['level'] = desired_level

            ao_data = json.dumps(ao_json)
            ao_update = requests.post(aspace_url+ao_uri,headers=headers,data=ao_data).json()

#print confirmation that archival object was updated. Response should contain any warnings
            row.append(ao_update['status'])
        except:
            print 'AO NOT FOUND: ' + ao_id
            row.append('ERROR: AO NOT FOUND')

        with open(output_csv,'ab') as csvout:
            writer = csv.writer(csvout)
            writer.writerow(row)
        #print a new line to the console, helps with readability
        print '\n'
print "All done"