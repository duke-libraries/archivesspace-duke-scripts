import csv
import requests
import json
import getpass

#Script slightly modified from script provided by Alicia Detelich, Yale Manuscripts and ArchivesSpace

#Script reads CSV input with following columns: resource record URI, note persistent ID, eadid, finding_aid_status, title, dates, new accessrestrict text
#Script will locate notes by note_PID (column 2) and replace existing note text with text from CSV (column 6)
#Script will write out log of actions to CSV file (updated_notes.csv) including: URI, note PID, eadid, finding_aid_status, updated text, success/failure

#Script will fail if resource record URI no longer exists...and probably for other reasons. Best to test in development.


def login():
    api_url = raw_input('Please enter the ArchivesSpace API URL: ')
    username = raw_input('Please enter your username: ')
    password = getpass.getpass(prompt='Please enter your password: ')
    auth = requests.post(api_url+'/users/'+username+'/login?password='+password+'&expiring=false').json()
    #if session object is returned then login was successful; if not it failed.
    if 'session' in auth:
        session = auth["session"]
        headers = {'X-ArchivesSpace-Session':session}
        print('Login successful! Hello ' + auth["user"]["name"])
        return (api_url, headers)
    else:
        print('Login failed! Check credentials and try again')
        exit()

def opencsv():
    '''This function opens a csv file'''
    input_csv = raw_input('Please enter path to input CSV: ')
    file = open(input_csv, 'rb')
    csvin = csv.reader(file)
    #Skip header row
    next(csvin, None)
    return csvin


def replace_note_by_id():
    #replaces a note's content in ArchivesSpace using a persistent ID
    values = login()
    csvfile = opencsv()
    spreadsheet = raw_input('Path to output CSV: ')
    print 'Creating a csv'
    writer = csv.writer(open(spreadsheet, 'wb'))
    #write a header row
    writer.writerow(["URI", "note_persistent_id", "eadid", "finding_aid_status", "note_text", "update_status"])

    for row in csvfile:
        record_uri = row[0]
        persistent_id = row[1]
        ead_id = row[2]
        finding_aid_status = row[3]
        note_text = row[6]
        resource_json = requests.get(values[0] + record_uri, headers=values[1]).json()
        for note in resource_json['notes']:
            if note['jsonmodel_type'] == 'note_multipart':
                if note['persistent_id'] == persistent_id:
                    note['subnotes'][0]['content'] = note_text
            elif note['jsonmodel_type'] == 'note_singlepart':
                if note['persistent_id'] == persistent_id:
                    note['content'] = [note_text]
        resource_data = json.dumps(resource_json, indent=4, sort_keys=True)
        row = []
        row.append(record_uri)
        row.append(persistent_id)
        row.append(ead_id)
        row.append(finding_aid_status)
        row.append(note_text)
        try:
            resource_update = requests.post(values[0] + record_uri, headers=values[1], data=resource_data).json()
            row.append(resource_update)
            print(resource_update)
        except:
            row.append('FAILURE')
            print('*****FAILURE*****')
            pass
        writer.writerow(row)
replace_note_by_id()
