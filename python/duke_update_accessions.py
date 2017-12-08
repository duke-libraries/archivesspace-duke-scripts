import requests
import json
import csv
import os
import getpass
import ConfigParser

# Script currently updates accession records, can be modified to target specific fields
# DO NOT INCLUDE HEADER ROW
# Column 1 contains the ASpace ID (from the URI)
# Column 2 contains the values to update


#AUTHENTICATION STUFF
#Prompt for backend URL ( e.g. http://localhost:8089) and login credentials
baseURL = raw_input('ASpace backend URL: ')
repository = raw_input('Repository number?: ')
username = raw_input('Username: ')
password = getpass.getpass(prompt='Password: ')

#Authenticate and get a session token
try:
    auth = requests.post(baseURL+'/users/'+username+'/login?password='+password).json()
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
#prompt for input file path for CSV with ASpace accession IDs in first column and second column for value to be updated
accession_updater_csv = raw_input("Path to input CSV: ")

#prompt for output path
# The updated_accessions_csv will be an updated csv that will be created at the end of this script, containing all of the same
# information as the starting csv, plus the ArchivesSpace URIs for the updated archival objects
accessions_updated_csv = raw_input("Path to output CSV: ")


#Open the CSV file and iterate through each row
with open(accession_updater_csv,'rb') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:

        # Grab the archival object's ArchivesSpace ref_id from the CSV
        accession_id = row[0] #column 1

        #Grab the value you want to update from the CSV
        updated_value = row[1] #column 2 in CSV

        #Grab the new date from the CSV
        #new_ao_date = row[2]

        #Lookup accession by URI
        #params = {"ref_id[]":ref_id}

        try:
          accession_json = requests.get(baseURL+'/repositories/'+repository+'/accessions/'+accession_id,headers=headers).json()
          #print accession_json

          accession_info = accession_json['title'].encode('utf-8')

          accession_uri = accession_json['uri']

          print accession_info

        ########UPDATE FIELD BELOW AS NECESSARY###################
          accession_json['collection_management']['processing_status'] = updated_value

          accession_data = json.dumps(accession_json)

          #Repost the archival object containing the new title
          accession_update = requests.post(baseURL+accession_uri,headers=headers,data=accession_data).json()

          #print confirmation that archival object was updated. Response should contain any warnings
          print 'Status: ' + accession_update['status']
          row.append(accession_update['status'])

          # Write a new CSV with all the info from the initial csv + the ArchivesSpace uris for the updated archival objects


        except:
          print 'ACCESSION NOT UPDATED'
          row.append('Accession Not Updated')
          pass

        with open(accessions_updated_csv,'ab') as csvout:
            writer = csv.writer(csvout)
            writer.writerow(row)
        #print a new line to the console, helps with readability
        print '\n'