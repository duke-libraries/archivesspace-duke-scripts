#/usr/bin/python3
#~/anaconda3/bin/python
from asnake.client import ASnakeClient
from asnake.aspace import ASpace
import asnake.logging as logging
import csv


#Used to remove expired restrictions notes from ArchivesSpace archival_objects (and maybe resources, eventually)
#Takes CSV input that is output of https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/sql/access_restriction_notes_on_aos.sql
#Looks up AO by ID, finds matching note using persistent ID value in CSV, deletes note, reposts AO

#Could probably refine this, add better logging...

logging.setup_logging(filename="remove_restrictions.log",filemode="a")
logger = logging.get_logger("remove_restrictions")

#Config
AS_username = '[username]'
AS_password = '[password]'
#AS_repository_id = '2'
AS_api_url = "[API URL]"

#Log into ASpace
aspace = ASpace(baseurl=AS_api_url,
                username=AS_username,
                password=AS_password)

aspace_client = ASnakeClient(baseurl=AS_api_url,
                             username=AS_username,
                             password=AS_password)
aspace_client.authorize()

input_csv = input("Input CSV: ")
output_csv = input("Output CSV: ")

with open(input_csv,'rt', newline='', encoding='utf-8') as csvfile, open(output_csv,'wt', newline='', encoding='utf-8') as csvout:
    csvin = csv.reader(csvfile)
    next(csvin, None) #ignore header row
    csvout = csv.writer(csvout)

    for i, row in enumerate(csvin):
        
        if(i >+ 10): #Testing with first 10 rows
           break
        
        #ID value only (not URI string)
        input_ao_id = row[4]
        #Note Persistent ID
        input_ao_note_pid = row[10]

        #AOs might belong to more then one repo
        AS_repository_id = row[0]
        
        #Lookup the AO
        ao_json = aspace_client.get('/repositories/{0}/archival_objects/{1}'.format(AS_repository_id, input_ao_id)).json()
        
        #Store original JSON to print to log as backup
        original_ao_json = ao_json
        
        print(ao_json['uri'])
        
        ao_title = ao_json['title']
        ao_ref_id = ao_json['ref_id']
        ao_uri = ao_json['uri']
        
        print("NOTES BEFORE REMOVAL")
        print(ao_json['notes'])
        
        
        #Find matching note in copy of note list and remove?
        for note in ao_json['notes'][:]:
            if note['jsonmodel_type'] == 'note_multipart':
                if note['persistent_id'] == input_ao_note_pid:
                    print("Deleting Matching Note")
                    deleted_note_id = note['persistent_id']
                    
                    #Remove matching note from list of notes
                    ao_json['notes'].remove(note)
                    
                    #Post back modified AO JSON
                    ao_update = aspace_client.post(ao_uri,json=ao_json).json()
                    
                    print(ao_update)
                    
                    row.append(ao_update)
                    
                    logger.info('remove_note', action='remove_note', data={'original_ao': original_ao_json, 'updated_ao': ao_json,'response': ao_update})
                    
        print("NOTES AFTER REMOVAL")
        print(ao_json['notes'])
        

        # Write a new csv with all the info from the initial csv with URIs, responses appended
        with open(output_csv,'at', newline='', encoding='utf-8') as csvout:
            writer = csv.writer(csvout)
            writer.writerow(row)
