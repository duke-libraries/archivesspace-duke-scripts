#/usr/bin/python3
#~/anaconda3/bin/python
from asnake.client import ASnakeClient
from asnake.aspace import ASpace
import asnake.logging as logging
import csv
import configparser

#USE FOR CREATING "STAND-IN" DOs in ASpace for groupings of born-digital items in DDR
#Takes as input a CSV of Archival Object ref_ID values in column 1
#For each ref_ID value, creates a new Digital Object in ASpace and links as instance of Archival Object with matching ref_ID
#Supplies basic metadata for the Digital Object 
#Writes output CSV and logfile of activity

logging.setup_logging(filename="create_dos_from_ddr_born-digital.log",filemode="a")
logger = logging.get_logger("born-digital-DOs")

#ASpace credentials and other variables stored in local config file
configFilePath = 'asnake_local_settings.cfg'
config = configparser.ConfigParser()
config.read(configFilePath)

#Read variables from asnake_local_settings.cfg
AS_username = config.get('ArchivesSpace','user')
AS_password = config.get('ArchivesSpace','password')
AS_api_url = config.get('ArchivesSpace','baseURL')
AS_repository_id = config.get('ArchivesSpace','repository')

#Log into ASpace
aspace = ASpace(baseurl=AS_api_url,
                username=AS_username,
                password=AS_password)

aspace_client = ASnakeClient(baseurl=AS_api_url,
                             username=AS_username,
                             password=AS_password)
aspace_client.authorize()

input_csv = input("Path to Input CSV: ")
output_csv = input("Path to Output CSV: ")
#Prompt for publishing digital objects and components (true or false)
publish_true_false = input("Publish Digital Objects? true or false?: ")


#Global Variables for all DOs created
file_version_use_statement = 'ddr-item-lookup'
#Set prefix for DDR search URLs
ddr_lookup_prefix = 'https://repository.duke.edu/catalog?f[common_model_name_ssi][]=Item&f[aspace_id_ssi][]='


with open(input_csv,'rt', newline='') as csvfile, open(output_csv,'wt', newline='') as csvout:
    csvin = csv.reader(csvfile)
    next(csvin, None) #ignore header row
    csvout = csv.writer(csvout)

    for row in csvin:

        # Grab the archival object's ArchivesSpace ref_id from the csv in first column
        ref_id = row[0]
     
        #Use default file_version_use_statement for all DOs
        file_version_use_statement = 'ddr-item-lookup'

        print ('Searching for ' + ref_id)

        repo = aspace.repositories(AS_repository_id)
        params = {"ref_id[]":ref_id}
        lookup = aspace_client.get('/repositories/{0}/find_by_id/archival_objects'.format(AS_repository_id), params=params).json()
        
        # Grab the archival object uri from the search results. It should be the first and only result
        archival_object_uri = lookup['archival_objects'][0]['ref']

        print ('Found AO: ' + archival_object_uri)

        #Get AO as JSON
        archival_object_json = aspace_client.get(archival_object_uri).json()

        # Continue only if the search-returned archival object's ref_id matches our starting ref_id, just to be safe
        # Note: probably no longer necessary when using the find_by_id endpoint
        if archival_object_json['ref_id'] == ref_id:

            # Add the archival object uri to the row from the csv to write it out at the end
            row.append(archival_object_uri)

            # Reuse the display string from the archival object as the digital object title
            display_string = archival_object_json['display_string']


            # Form the digital object JSON using values from CSV and Global variables
            dig_obj_json = {'title':display_string,'digital_object_id':ref_id,'file_versions':[{'file_uri':ddr_lookup_prefix + ref_id,'use_statement':file_version_use_statement}]}
            
            # Post the digital object
            dig_obj_post = aspace_client.post('/repositories/{0}/digital_objects'.format(AS_repository_id), json=dig_obj_json).json()
            logger.info('post_digital_object', action='DO_post', data={'record': dig_obj_json,'response': dig_obj_post})
            
            print ('Digital Object Status: ', dig_obj_post['status'])

            # Grab the digital object uri
            dig_obj_uri = dig_obj_post['uri']

            print ('Digital Object URI: ', dig_obj_uri)

            #publish the digital object
            if publish_true_false == 'true':
                print ('Publishing: ' + dig_obj_uri)
                dig_obj_publish_all = aspace_client.post(dig_obj_uri + '/publish')

            # Add the digital object uri to the row from the csv to write it out at the end
            row.append(dig_obj_uri)

            # Build a new instance to add to the archival object, linking to the digital object
            dig_obj_instance = {'instance_type':'digital_object', 'digital_object':{'ref':dig_obj_uri}}

            # Append the new instance to the existing archival object record's instances
            archival_object_json['instances'].append(dig_obj_instance)
            
            # Repost the archival object
            archival_object_update = aspace_client.post(archival_object_uri,json=archival_object_json).json()
            logger.info('update_archival_object', action='AO_update', data={'record': archival_object_json,'response': archival_object_update})

            print ('Archival Object Status: ' + archival_object_update['status'])

            # Write a new csv with all the info from the initial csv + the ArchivesSpace uris for the archival and digital objects
            with open(output_csv,'at', newline='') as csvout:
                writer = csv.writer(csvout)
                writer.writerow(row)

            #print a new line for readability in console
            print ('\n')