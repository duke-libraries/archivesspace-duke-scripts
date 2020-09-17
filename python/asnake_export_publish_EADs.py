import io
import time
import requests
import configparser
from asnake.client import ASnakeClient
from asnake.aspace import ASpace

#This Script takes as user input a comma separated list of EADID values and does the following:
#1) Checks to see if the ASpace resource record has an ARK in the ead_location field
#2) If not, it mints a new ARK, sets the target of the ARK to the ArcLight URL, and POSTs the ARK to ead_location field
#3) Checks the resource records tree for any unpublished nodes. If any found, the script stops
#4) Prints out any text in the Repository Processing Note field. If any text, found, user must confirm to proceed
#5) Sets the finding aid status value to "published" if it's not published already
#6) Exports the EAD file and saves to specified location (EAD_export_path) using EADID.xml as filename


#ASpace credentials and other variables stored in local config file
configFilePath = 'asnake_local_settings.cfg'
config = configparser.ConfigParser()
config.read(configFilePath)

#Read variables from anake_local_settings.cfg
AS_username = config.get('ArchivesSpace','user')
AS_password = config.get('ArchivesSpace','password')
AS_api_url = config.get('ArchivesSpace','baseURL')
AS_repository_id = config.get('ArchivesSpace','repository')
EAD_export_path = config.get('EADexport','exportPath')
EZID_username = config.get('EZID', 'ezid_username')
EZID_password = config.get('EZID', 'ezid_password')
ARK_shoulder = config.get('EZID', 'ark_shoulder')
ARK_owner = config.get('EZID', 'ark_owner')

#set EAD export options: number components and include DAOs
export_options = '?include_daos=true&numbered_cs=true&include_unpublished=false'


#Log Into ASpace
aspace = ASpace(baseurl=AS_api_url,
                username=AS_username,
                password=AS_password)

aspace_client = ASnakeClient(baseurl=AS_api_url,
                             username=AS_username,
                             password=AS_password)
aspace_client.authorize()

# Prompt for input, a comma separated list of EADID values (e.g. johndoepapers, janedoepapers, johnandjanedoepapers)
eadids = input("List of EADIDs:  ")
# Split comma separated list
eadids_list = eadids.split(",")

#Check ead_location field for presence of ARK-like URL
def aspace_ark_check(resource_uri):
    ark_check = aspace_client.get(resource_uri).json()
    try:
        ead_location = ark_check['ead_location']
        if "ark:" in ead_location:
            print (eadID + " | ARK already assigned")
            return True
        else:
            print (eadID + " | Non ARK URL - Needs a new ARK")
            return False
    except:
        print (eadID + " | No EAD Location value - Needs an ARK")
        return False

#Mint new ARK and POST to ASpace
def mint_and_post_new_ark(eadID):
     
    #Set ArcLight URL prefix as target URL base + EADID (should come from AS resource record) and assign owner as "duke_ddr"
    ark_data = '_target: https://archives.lib.duke.edu/catalog/{0}\n_owner: {1}'.format(eadID, ARK_owner)
    
    #EZID seems to need these headers to be explicit
    headers = {'Content-type': 'text/plain; charset=UTF-8'}
    
    print (eadID + " | Minting an ARK...")
    
    try: 
        mint_ark = requests.post('https://ezid.cdlib.org/shoulder/{0}'.format(ARK_shoulder), headers=headers, data=ark_data, auth=(EZID_username, EZID_password))
        #below for testing
        #mint_ark = requests.post('https://ezid.cdlib.org/shoulder/ark:/99999/fk4', headers=headers, data=ark_data, auth=(EZID_username, EZID_password))
        
        #responses look like (success: ark:/99999/fk4jm3mb69)
        mint_response_text = mint_ark.text
        
        #convert response to a Dict (e.g. {'success': 'ark:/99999/fdkl;jlkj'})
        mint_response_dict = dict(mint_response_text.split(': ',1) for line in mint_response_text.strip().split('\n'))
        
        #print (mint_response_dict['success'])
        minted_ark = mint_response_dict['success']
        #print (minted_ark)
        
        #get metadata about the ARK you just minted...
        get_minted_ark = requests.get('https://ezid.cdlib.org/id/{0}'.format(minted_ark), auth=(EZID_username, EZID_password))
        print (get_minted_ark.text)
        
        #Prepend Duke URL stuff to beginning of ARK
        full_ark_uri = "https://idn.duke.edu/{0}".format(minted_ark)
        print (eadID + " | Minted ARK: " + full_ark_uri)
        
        #Get ASpace resource record
        resource_json = aspace_client.get(resource_uri).json()
        
        #Overwrite existing ead_location field value with new ARK URL
        resource_json['ead_location'] = full_ark_uri
        
        #Post updated ARK
        resource_update_ark = aspace_client.post(resource_uri, json=resource_json).json()
        print (eadID + " | Writing ARK to ASpace: " + resource_update_ark['status'])
    
    except:
        print (eadID + " | ERROR with ARK Minting / Posting")


#Checking if any unpublished nodes in the tree
def check_for_unpublished_nodes():
    print(eadID + " | checking for any unpublished children in the tree...")
    rl_repo = aspace.repositories(AS_repository_id)
    resource_record = rl_repo.resources(aspace_id_num_only).tree
    resource_tree = resource_record.walk
    node_test = []
    for node in resource_tree:
        if node.publish == False:
            print (eadID + " | " + "UNPUBLISHED NODE: " + node.uri + " " + node.title)
            node_test.append("True")
        else:
            node_test.append("")
    #print (node_test)
    if "True" in node_test:
        print (eadID + " | Review Unpublished Nodes Above")
        return True
    else:
        print (eadID + " | All Nodes Published")
        return False


#Exports EAD for all resources matching EADID input in repository
for eadid in eadids_list:
 
#advanced search for EADID    
    results = aspace_client.get('repositories/'+AS_repository_id+'/search?page=1&aq={\"query\":{\"field\":\"ead_id\",\"value\":\"'+eadid+'\",\"jsonmodel_type\":\"field_query\",\"negated\":false,\"literal\":false}}').json()
    
    if results["total_hits"] != 0:
        #get the URI of the first search result (should only be one)
        uri = results["results"][0]["id"]
        #get JSON for the resource based on above URI
        resource_json = aspace_client.get(uri).json()
        #get URI of Resource record
        resource_uri = resource_json["uri"]
        #replace /resources with /resource_descriptions for EAD export
        id_uri_string = resource_uri.replace("resources","resource_descriptions")
        #get user who last modified record (just print it out to the console on export confirmation)
        last_modified_by = results["results"][0]["last_modified_by"]
        #get last modified time (just print it out to console on export confirmation)
        user_mtime_full = results["results"][0]["user_mtime"]
        #remove timestamp from date - day is good enough
        user_mtime_slice = user_mtime_full[0:10]
        #get resource ID (just print out to console on export confirmation)
        resource_id = results["results"][0]["identifier"]
        aspace_id_full = results["results"][0]["id"]
        #shorten the identifier to resources/#
        aspace_id_short = aspace_id_full.replace("/repositories/2/","")
        aspace_id_num_only = aspace_id_short.replace("resources/","")
        #get the EADID value for printing
        eadID = resource_json["ead_id"]
        #set publish_status variable to check for finding aid status values
        publish_status = resource_json["finding_aid_status"]

        #If the resource has a repository processing note, print it out to console. Confirm that you want to proceed with publishing
        try:
            repository_processing_note = resource_json["repository_processing_note"]
            repository_processing_note != None
            print (eadID + " | WARNING - Repository Processing Note: " + repository_processing_note)
            raw_input = input("Proceed anyway? y/n?")
            if raw_input == "n":
                break
            else:
                pass
        except:
            pass

        
        #Check for ARK, if none, mint new ARK and POST to ASpace
        if aspace_ark_check(resource_uri) == False:
            mint_and_post_new_ark(eadID)
        else:
            pass
        
        
        #Test for unpublished nodes, if none continue with publishing
        if check_for_unpublished_nodes() == False:

            #If the finding aid status is already set to publish, just export the EAD
            if "published" in publish_status:
            # Set publish to 'true' for all levels, components, notes, etc.  Same as choosing "publish all" in staff UI
                resource_publish_all = aspace_client.post(resource_uri + '/publish')
                print (eadID + ' | resource and all children set to published')
            #Pause for 5 seconds so publish action takes effect
                print (eadid + " | Pausing for 10 seconds to index publish action...")
                time.sleep(10.0)
                print (eadID + " | Exporting EAD file...")
                ead = aspace_client.get(id_uri_string + '.xml' + export_options).text
                f = io.open(EAD_export_path + eadID +'.xml', mode='w', encoding='utf-8')
                f.write(ead)
                f.close()
                print (eadID + '.xml' ' | ' + resource_id + ' | ' + aspace_id_short + ' | ' + last_modified_by + ' | ' + user_mtime_slice + ' | ' + 'exported')
    
            #If not published, set finding aid status to published
            else:
                print (eadID + " | Finding aid status: " + publish_status)
                resource_publish_all = aspace_client.post(resource_uri + '/publish')
                print (eadID + ' | resource and all children set to published')
                print (eadID + " | Pausing for 5 seconds to index publish action...")
                time.sleep(5.0)
                resource_json['finding_aid_status'] = 'published'
                #resource_data = json.dumps(resource_json)
                #Repost the Resource with the published status
                resource_update = aspace_client.post(resource_uri, json=resource_json).json()
                print (eadID + ' | reposted resource with finding aid status = published')
            #Pause for 5 seconds so publish action takes effect
                print (eadID + " | Pausing for 5 seconds to index reposted resource...")
                time.sleep(5.0)
                print (eadID + " | Exporting EAD file...")
                ead = aspace_client.get(id_uri_string + '.xml' + export_options).text
                f = io.open(EAD_export_path + eadID + '.xml', mode='w', encoding='utf-8')
                f.write(ead)
                f.close()
                print (eadID + '.xml' ' | ' + resource_id + ' | ' + aspace_id_short + ' | ' + last_modified_by + ' | ' + user_mtime_slice + ' | ' + 'exported')

        else:
            print(eadID + " | STOPPING - please review unpublished nodes in " + eadID)
    else:
        print (eadID + ' | ***ERROR***: ' + eadid + ' does not exist!')

input("All done!. Press Enter to Exit")