#!/usr/bin/env python3

import requests
import re
import csv
import sys
import time
import io
import configparser
import argparse
import xml.dom.minidom


DEBUG = False

configFilePath = 'asnake_local_settings.cfg'
config = configparser.ConfigParser()
config.read(configFilePath)

# Read variables from asnake_local_settings.cfg
AS_username = config.get('ArchivesSpace', 'user')
AS_password = config.get('ArchivesSpace', 'password')
AS_api_url = config.get('ArchivesSpace', 'baseURL')
AS_repository_id = config.get('ArchivesSpace', 'repository')
EAD_export_path = config.get('EADexport', 'exportPath')
EZID_username = config.get('EZID', 'ezid_username')
EZID_password = config.get('EZID', 'ezid_password')
ARK_shoulder = config.get('EZID', 'ark_shoulder')
ARK_owner = config.get('EZID', 'ark_owner')

# set EAD export options: number components and include DAOs
export_options = '?include_daos=true&numbered_cs=true&include_unpublished=false'

# Log Into ASpace
print('Logging into ' + AS_api_url)
print('As user: ' + AS_username)
startTime = time.time()

response = requests.post(AS_api_url + '/users/' + AS_username+ '/login?password='
                     + AS_password)
if response.status_code == 200:
    response_json = response.json()
    if DEBUG:
        print("DEBUG======================DEBUG")
        print(f'Response text: \n {response_json}')
        print("DEBUG======================DEBUG")
    print('Login successful! Continuing process.')
else:
    print(f'Login failed! Response text: \n {response.text}')
    print('Exiting process.')
    exit()

session = response_json['session']
headers = {'X-ArchivesSpace-Session': session,
           'Content_Type': 'application/json'}

endpoint = '/repositories/' + AS_repository_id + '/resources?all_ids=true'

def get_ead(resource_uri):
    """Get EAD ID from resource URI"""
    response = requests.get(AS_api_url + resource_uri, headers=headers).json()
    ead = response['ead_id']
    if DEBUG:
        print("DEBUG======================DEBUG")
        print(f'ead_id for resource {resource_uri}: {ead}')
        print("DEBUG======================DEBUG")
    return ead


def get_resource_uri(ead_id):
    """Get resource uri from ead_id"""
    # Ask Mary about pages?
    response = requests.get(AS_api_url + '/repositories/'+ AS_repository_id +'/search?page=1&aq={"query":{"field":"ead_id","value":"'+ead_id+'","jsonmodel_type":"field_query","negated":false,"literal":false}}', headers=headers).json()
    resource_uri = response['results'][0]['uri']
    if DEBUG:
        print("DEBUG======================DEBUG")
        print(f'Response: {response}')
        print(f'resource_uri for {ead_id}: {resource_uri}')
        print("DEBUG======================DEBUG")
    return resource_uri


def aspace_ark_check(resource_uri, ead_id):
    """check for existing ARK"""
    resource_json = requests.get(AS_api_url + resource_uri, headers=headers).json()
    print(f'ARK check for {ead_id} : {resource_uri}')
    try:
        ead_location = resource_json['ead_location']
        if DEBUG:
            print("DEBUG======================DEBUG")
            print(f'JSON for {ead_id} : {resource_uri}: {resource_json}')
            print(f'ead_location for {ead_id} : {resource_uri}: {ead_location}')
            print("DEBUG======================DEBUG")
        if "ark:" in ead_location:
            print(f'ARK already exists for {ead_id} : {resource_uri}')
            return True
        else:
            print(f'ead_location exists for {ead_id} : {resource_uri} but no ARK')
            return False
    except:
        print(f'No ead_location for {ead_id} : {resource_uri}')
        return False


def mint_and_post_new_ark(resource_uri, ead_id):
    """Mint new ARK and POST to ASpace"""
    #Set ArcLight URL prefix as target URL base + EADID (should come from AS resource record) and assign owner as "duke_ddr"
    ark_data = '_target: https://archives.lib.duke.edu/catalog/{0}\n_owner: {1}'.format(ead_id, ARK_owner)
    #EZID seems to need these headers to be explicit
    headers = {'Content-type': 'text/plain; charset=UTF-8'}
    print (ead_id + " | Minting an ARK...")
    try:
        mint_ark = requests.post('https://ezid.cdlib.org/shoulder/{0}'.format(ARK_shoulder), headers=headers, data=ark_data, auth=(EZID_username, EZID_password))
        #mint_ark = requests.post('https://ezid.cdlib.org/shoulder/ark:/99999/fk4', headers=headers, data=ark_data, auth=(EZID_username, EZID_password))
        #responses look like (success: ark:/99999/fk4jm3mb69)
        mint_response_text = mint_ark.text
        #convert response to a Dict (e.g. {'success': 'ark:/99999/fdkl;jlkj'})
        mint_response_dict = dict(mint_response_text.split(': ',1) for line in mint_response_text.strip().split('\n'))
        minted_ark = mint_response_dict['success']
        #get metadata about the ARK you just minted...
        get_minted_ark = requests.get('https://ezid.cdlib.org/id/{0}'.format(minted_ark), auth=(EZID_username, EZID_password))
        print (get_minted_ark.text)
        #Prepend Duke URL stuff to beginning of ARK
        full_ark_uri = "https://idn.duke.edu/{0}".format(minted_ark)
        print (ead_id + " | Minted ARK: " + full_ark_uri)
        #Get ASpace resource record
        #resource_json = aspace_client.get(resource_uri).json()
        resource_json = requests.get(AS_api_url + resource_uri, headers=headers).json()
        #Overwrite existing ead_location field value with new ARK URL
        resource_json['ead_location'] = full_ark_uri
        #Post updated ARK
        #resource_update_ark = aspace_client.post(resource_uri, json=resource_json).json()
        resource_update_ark = requests.post(AS_api_url + resource_uri, headers=headers, json=resource_json).json()
        print (ead_id + " | Writing ARK to ASpace: " + resource_update_ark['status'])
        if DEBUG:
            print("DEBUG======================DEBUG")
            print (mint_response_text)
            print (mint_response_dict)
            print (minted_ark)
            print("DEBUG======================DEBUG")
    except:
        print (ead_id + " | ERROR with ARK Minting / Posting")


def check_for_unpublished_nodes(resource_uri, ead_id):
    """TODO: Check for unpublished nodes in the tree"""
    print(ead_id + " | checking for any unpublished children in the tree...")
    #rl_repo = aspace.repositories(AS_repository_id)
    rl_repo = requests.get(AS_api_url + '/repositories/' + AS_repository_id, headers=headers).json()
    resource_id = resource_uri.split('/')[-1]
    #print(resource_id)
    #resource_record = requests.get(AS_api_url + '/repositories/' + AS_repository_id + '/resources/' + resource_id + '/tree?node_uri=/repositories/2/archival_objects/5', headers=headers).json()
    #print (resource_record)
    ##uri_list = requests.get(AS_api_url + '/repositories/' + AS_repository_id + '/resources/' + resource_id + '/ordered_records', headers=headers).json()
    ##print(uri_list)
    ###tree_path = requests.get(AS_api_url + '/repositories/' + AS_repository_id + '/resources/' + resource_id + '/tree/node_from_root?node_ids[]=' + resource_id, headers=headers).json()
    ###print(tree_path)
    ##tree_root = requests.get(AS_api_url + '/repositories/' + AS_repository_id + '/resources/' + resource_id + '/tree/root', headers=headers).json()
    ##print(tree_root)
    #tree = requests.get(AS_api_url + '/repositories/' + AS_repository_id + '/resources/' + resource_id + '/tree', headers=headers).json()
    #print(tree)
    # Classification not found
    #tree_info = requests.get(AS_api_url + '/repositories/' + AS_repository_id + '/classifications/' + resource_id + '/tree/node?node_uri=/repositories/2/classification_terms/' + resource_id, headers=headers).json()
    # Can throw in an archival object
    #tree_info = requests.get(AS_api_url + '/repositories/' + AS_repository_id + '/resources/' + resource_id + '/tree/node?node_uri=/repositories/2/archival_objects/163995', headers=headers).json()
    #print(tree_info)
    return False
   # resource_record = rl_repo.resources(aspace_id_num_only).tree
   # resource_tree = resource_record.walk
   # node_test = []
   # for node in resource_tree:
   #     if node.publish == False:
   #         print (ead_id + " | " + "UNPUBLISHED NODE: " + node.uri + " " + node.title)
   #         node_test.append("True")
   #     else:
   #         node_test.append("")
   # #print (node_test)
   # if "True" in node_test:
   #     print (ead_id + " | Review Unpublished Nodes Above")
   #     return True
   # else:
   #     print (ead_id + " | All Nodes Published")
   #     return False



ids = requests.get(AS_api_url+ endpoint, headers=headers).json()

input_eads = input('Type out EAD ID to check for ARK (comma separated): ')
input_eads = [x.strip() for x in input_eads.split(',')]
input_uris = []
#if all(i.isnumeric() for i in input_eads):
#    print(f'Interpretting your input as URIs')
#    input_uris = input_eads
#    input_uris = list(map(lambda x: '/repositories/2/resources/' + x, input_uris))
#    input_eads = map(lambda x: get_ead(x), input_uris)
#    input_eads = list(input_eads)
#    if DEBUG:
#        print("DEBUG======================DEBUG")
#        print(f'input_uris: {input_uris}')
#        print("DEBUG======================DEBUG")
#if all(i.isalpha() for i in input_eads):
#    print(f'Interpretting your input as EAD IDs')
#    if DEBUG:
#        print("DEBUG======================DEBUG")
#        print(f'input_eads: {input_eads}')
#        print("DEBUG======================DEBUG")
#else:
#    print(f'Do not mix EAD IDs and URIs!')
#    if DEBUG:
#        print("DEBUG======================DEBUG")
#        print(f'Here is what you entered, run separately: {input_eads}')
#        print("DEBUG======================DEBUG")
#    sys.exit()

#get_ead('/repositories/2/resources/1234')
# thought process is always going to be provide a list of ead_ids and if uri is provided, convert to ead_id:
print(f'input_eads: {input_eads}')
for ead in input_eads:
    #get_resource_uri(ead)
    #aspace_ark_check(get_resource_uri(ead), ead)
    #mint_and_post_new_ark(get_resource_uri(ead), ead)
    #check_for_unpublished_nodes(ead)

    response = requests.get(AS_api_url + '/repositories/'+ AS_repository_id +'/search?page=1&aq={"query":{"field":"ead_id","value":"'+ead+'","jsonmodel_type":"field_query","negated":false,"literal":false}}', headers=headers).json()
    if DEBUG:
        print(response['total_hits'])
    if response['total_hits'] != 0:
        uri = response["results"][0]["id"]
        print(f'URI: {uri}')
        resource_json = requests.get(AS_api_url + uri, headers=headers).json()
        resource_uri = resource_json['uri']
        print(f'resource_uri: {resource_uri}')
        #replace /resources with /resource_descriptions for EAD export
        id_uri_string = resource_uri.replace("resources","resource_descriptions")
        print(f'id_uri_string: {id_uri_string}')
        #get user who last modified record (just print it out to the console on export confirmation)
        last_modified_by = response["results"][0]["last_modified_by"]
        print(f'last_modified_by: {last_modified_by}')
        #get last modified time (just print it out to console on export confirmation)
        user_mtime_full = response["results"][0]["user_mtime"]
        print(f'user_mtime_full: {user_mtime_full}')
        #remove timestamp from date - day is good enough
        user_mtime_slice = user_mtime_full[0:10]
        print(f'user_mtime_slice: {user_mtime_slice}')
        #get resource ID (just print out to console on export confirmation)
        resource_id = response["results"][0]["identifier"]
        print(f'resource_id: {resource_id}')
        aspace_id_full = response["results"][0]["id"]
        print(f'aspace_id_full: {aspace_id_full}')
        #shorten the identifier to resources/#
        aspace_id_short = aspace_id_full.replace("/repositories/2/","")
        print(f'aspace_id_short: {aspace_id_short}')
        aspace_id_num_only = aspace_id_short.replace("resources/","")
        print(f'aspace_id_num_only: {aspace_id_num_only}')
        publish_status = resource_json["finding_aid_status"]
        print(f'publish_status: {publish_status}')

        #If the resource has a repository processing note, print it out to console. Confirm that you want to proceed with publishing
        try:
            repository_processing_note = resource_json["repository_processing_note"]
            if repository_processing_note != None:
                print (ead + " | WARNING - Repository Processing Note: " + repository_processing_note)
                raw_input = input("Proceed anyway? y/n?")
                if raw_input == "n":
                    break
                else:
                    pass
        except:
            print (ead + " | No Repository Processing Note")
            pass

        if aspace_ark_check(resource_uri, ead) == False:
            mint_and_post_new_ark(resource_uri, ead)
        else:
            pass

        if check_for_unpublished_nodes(resource_uri, ead) == False:

            #If the finding aid status is already set to publish, just export the EAD
            if "published" in publish_status:
            # Set publish to 'true' for all levels, components, notes, etc.  Same as choosing "publish all" in staff UI
                #resource_publish_all = aspace_client.post(resource_uri + '/publish')
                resource_publish_all = requests.post(AS_api_url + resource_uri + '/publish', headers=headers).json()
                print (ead + ' | resource and all children set to published')
            #Pause for 5 seconds so publish action takes effect
                print (ead + " | Pausing for 10 seconds to index publish action...")
                time.sleep(10.0)
                print (ead + " | Exporting EAD file...")
                #ead = aspace_client.get(id_uri_string + '.xml' + export_options).text

                ead_xml = requests.get(AS_api_url + id_uri_string + '.xml' + export_options, headers=headers).text
                f = io.open(EAD_export_path + ead +'.xml', mode='w', encoding='utf-8')
                temp = xml.dom.minidom.parseString(ead_xml)
                pretty_xml_as_string = temp.toprettyxml()
                f.write(pretty_xml_as_string)
                f.close()

                print (ead + '.xml' ' | ' + resource_id + ' | ' + aspace_id_short + ' | ' + last_modified_by + ' | ' + user_mtime_slice + ' | ' + 'exported')

            #If not published, set finding aid status to published
            else:
                print (ead + " | Finding aid status: " + publish_status)
                #resource_publish_all = aspace_client.post(resource_uri + '/publish')
                resource_publish_all = requests.post(AS_api_url + resource_uri + '/publish', headers=headers).json()
                print (ead + ' | resource and all children set to published')
                print (ead + " | Pausing for 5 seconds to index publish action...")
                time.sleep(5.0)
                resource_json['finding_aid_status'] = 'published'
                #resource_data = json.dumps(resource_json)
                #Repost the Resource with the published status
                #resource_update = aspace_client.post(resource_uri, json=resource_json).json()
                resource_update = requests.post(AS_api_url + resource_uri, headers=headers, json=resource_json).json()
                print (ead + ' | reposted resource with finding aid status = published')
            #Pause for 5 seconds so publish action takes effect
                print (ead + " | Pausing for 5 seconds to index reposted resource...")
                time.sleep(5.0)
                print (ead + " | Exporting EAD file...")
                #ead = aspace_client.get(id_uri_string + '.xml' + export_options).text
                ead_xml = requests.get(AS_api_url + id_uri_string + '.xml' + export_options, headers=headers).text
                f = io.open(EAD_export_path + ead + '.xml', mode='w', encoding='utf-8')
                temp = xml.dom.minidom.parseString(ead_xml)
                pretty_xml_as_string = temp.toprettyxml()
                f.write(pretty_xml_as_string)
                f.close()
                print (ead + '.xml' ' | ' + resource_id + ' | ' + aspace_id_short + ' | ' + last_modified_by + ' | ' + user_mtime_slice + ' | ' + 'exported')

        else:
            print(ead + " | STOPPING - please review unpublished nodes in " + ead + " before proceeding")
    else:
        print (ead + ' | ***ERROR***: ' + ead + ' does not exist!')

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
