import requests
import json
import csv
import os
import getpass


#Script currently reads a CSV and updates archival object with link to a different top container.
#Used to batch update container numbers when material is reboxed, etc.
#Workflow: 
	#1) run SQL query to get two column CSV of AO URIs and old top container URIs
	#2) create a new top container in ASpace staff UI if necessary
	#3) add new top container URI in column 3 of CSV
	#4) Run this script, examine output CSV


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


ao_container_updates_csv = raw_input('Path to input CSV: ')
ao_containers_updated_csv = raw_input('Path to output CSV: ')

#Open the input CSV file and iterate through each row
with open(ao_container_updates_csv,'rb') as csvfile:
    reader = csv.reader(csvfile)
    next(csvfile, None) #ignore header row
    for row in reader:

        #Get info from CSV
        ao_uri = row[0] #column 1
        old_top_container_uri = row[1]
        new_top_container_uri = row[2] 

        ao = requests.get(aspace_url + ao_uri,headers=headers).json()
        ao_title = ao['title'].encode("utf-8")
        print ao_title
        existing_top_container = ao['instances'][0]['sub_container']['top_container']['ref']
        if existing_top_container == old_top_container_uri:
            ao['instances'][0]['sub_container']['top_container']['ref'] = new_top_container_uri
            ao_data = json.dumps(ao)
            ao_update = requests.post(aspace_url+ao_uri,headers=headers,data=ao_data).json()
      #print confirmation that archival object was updated. Response should contain any warnings
            print 'Status: ' + ao_update['status']
            row.append(ao_update['status'])
        else:
            print 'ERROR: OLD TOP CONTAINER IN CSV DOES NOT MATCH'
            row.append('OLD TOP CONTAINER IN CSV DOES NOT MATCH')

        with open(ao_containers_updated_csv,'ab') as csvout:
            writer = csv.writer(csvout)
            writer.writerow(row)
        #print a new line to the console, helps with readability
        print '\n'
print "All done"