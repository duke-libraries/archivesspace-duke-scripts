import requests
import json
import csv
import os
import getpass


#Script currently takes a CSV as input (with DO identifier in first column) and publishes or unpublishes the DO--as specified in script on line 64.

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
        do_identifier = row[0]

        print 'Looking up Digital Object: ' + do_identifier

        try:
            # Use the find_by_id endpoint (only available in v1.5+) to retrieve the digital object by identifier
            params = {"digital_object_id[]":do_identifier}
            lookup = requests.get(aspace_url+'/repositories/2/find_by_id/digital_objects',headers=headers, params=params).json()

            # Grab the digital object uri from the search results. It should be the first and only result...I think
            digital_object_uri = lookup['digital_objects'][0]['ref']

            print 'Found DO: ' + digital_object_uri

            # Submit a get request for the digital object and store the JSON
            digital_object_json = requests.get(aspace_url+digital_object_uri,headers=headers).json()

            #CHANGE AS APPROPRIATE (True=publish or False=unpublish)
            digital_object_json['publish'] = False

            digital_object_data = json.dumps(digital_object_json)
            do_update = requests.post(aspace_url+digital_object_uri,headers=headers,data=digital_object_data).json()

            print 'Status: ' + do_update['status']
            #print confirmation that digital object was updated. Response should contain any warnings
            row.append(do_update['status'])
        except:
            print 'OBJECT NOT FOUND: ' + do_identifier
            row.append('ERROR: OBJECT NOT FOUND')

        with open(output_csv,'ab') as csvout:
            writer = csv.writer(csvout)
            writer.writerow(row)
        #print a new line to the console, helps with readability
        print '\n'
print "All done"