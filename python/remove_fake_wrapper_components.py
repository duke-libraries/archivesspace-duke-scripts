#This script flattens the Resource tree in cases where there is a single "fake" wrapper component
#Prior to running script, run SQL query on AS database to obtain AO ids for fake wrapper components (e.g. title = "container list")

#When executed, this script:
#1) iterates over input CSV of archival object IDs
#2) checks to make sure the input AOs are the only direct children of a resource record
#3) locates the direct child components of the input AOs and their positions
#4) Posts those children back as direct children of the resource record (and not the AO)
#5) Deletes the fake wrapper AO component
#6) Checks to see if resource's finding aid status= published. If so, exports EAD and saves to location
#7) Outputs a CSV that includes all data in original CSV plus some additional columns for reporting

#DB Query:
# SELECT 
#     ao.root_record_id as resource_id, resource.title as collection_title, ao.id as ao_id, ao.title as ao_title
# FROM
#     archival_object ao
#     left join 
# 		resource on ao.root_record_id = resource.id	
# WHERE
#     ao.title LIKE '%Container List%'

import csv
import io
import time
from datetime import datetime
from asnake.client import ASnakeClient
from asnake.aspace import ASpace

import asnake.logging as logging
logging.setup_logging(level='DEBUG', filename="remove_fake_wrapper.log", filemode="a")


aspace = ASpace(baseurl="[ASPACE API URL]",
                      username="[USERNAME]",
                      password="[PASSWORD]")

#Log Into ASpace and set repo to RL
aspace_client = ASnakeClient(baseurl="[ASPACE API URL]",
                      username="[USERNAME]",
                      password="[PASSWORD]")
aspace_client.authorize()
#Set target repo
repo = aspace_client.get("repositories/2").json()
print("Logged into: " + repo['name'])

rl_repo = aspace.repositories(2)

#input is output of SQL query above
input_csv = input("Path to CSV Input: ")
#output will be input CSV plus some extra columns for reporting on actions taken, errors, etc.
updated_resources_csv = input("Path to CSV Output: ")


#Test if more than one direct child of Resource Object
#Why? Don't want to assign all children to Resource if there are other sibling Components of the fake wrapper component
def only_one_direct_child_of_resource_test(resource_object):
    print ("Checking for multiple top-level AOs...")
    resource_object = rl_repo.resources(row[0])
    resource_object_walk = resource_object.tree.walk
    aos_without_parents = []
    for ao in resource_object_walk:
    #TIL: Walking resource also returns the resource record itself
        ao_json = aspace_client.get(ao.uri).json()
        #print (ao_json)
        try:
            parent_ref = ao_json['parent']['ref']
        except:
            aos_without_parents.append(ao.uri)
    print("First Level AOs: " + str(aos_without_parents))
    if len(aos_without_parents) > 2: #resource object and first-level AO should be only ones without parents
        return False
    else:
        return True
                
#If Resource finding aid status = published, export the EAD for the resource, save to folder
def if_published_export_EAD(resource_object):
    resource_json = aspace_client.get(resource_object.uri).json()
    published_status = resource_json['finding_aid_status']
    id_uri_string = resource_json['uri'].replace("resources","resource_descriptions")
    #set EAD export options: number components and include DAOs
    export_options = '?include_daos=true&numbered_cs=true&include_unpublished=false'
    destination = 'C:/users/nh48/desktop/as_exports_temp/'
    eadid = resource_json['ead_id']
    if published_status == 'published':
        #wait 10 seconds for indexing
        time.sleep(10.0)
        ead = aspace_client.get(id_uri_string + '.xml' + export_options).text
        f = io.open(destination + eadid + '.xml', mode='w', encoding='utf-8')
        f.write(ead)
        f.close()
        print("EAD Exported\n===============================")
        row.append(eadid + " | Exported")
    else:
        print ("EAD NOT Exported - Finding Aid Status NOT PUBLISHED\n++++++++++++++++++++++++++++")
        row.append(eadid + " | UNPUBLISHED: EAD NOT Exported")


#Open CSV produced by SQL query and start processing
with open(input_csv,'rt', encoding='utf-8') as csvfile, open(updated_resources_csv,'wt') as csvout:
    csvin = csv.reader(csvfile)
    next(csvin, None) #ignore header row
    csvout = csv.writer(csvout)
    
    for row in csvin:
        resource_id = row[0]
        print ("Processing Resource: " + resource_id)
        resource_object = rl_repo.resources(row[0])
        fake_wrapper_ao = rl_repo.archival_objects(row[2])        
        
        #if only_one_direct_child_of_resource_test(resource_object) == True:
        if only_one_direct_child_of_resource_test(resource_object) == True:
            print("Collection has ONLY 1 top level AO")
            row.append("1 top-level AO")
        
            
            #print collection title and fake wrapper component info
            #print ("Collection: " + resource_object.title)
            print ("Fake Wrapper Component: " + fake_wrapper_ao.title + " | " + fake_wrapper_ao.uri)
      
            #Get Tree of Fake Wrapper Component
            fake_wrapper_ao_tree = fake_wrapper_ao.tree

            #Walk to AO tree
            fake_wrapper_ao_tree_walk = fake_wrapper_ao_tree.walk
        
            #Open a dictionary to store URIs and positions AOs that are direct children fake wrapper AOs
            children_of_fake_wrapper_component_dict = {}
        
            #Test each node in tree. If node is a direct child of Fake Wrapper AO, save node URI and Position to Dict
            for node in fake_wrapper_ao_tree_walk:
                child_node = aspace_client.get(node.uri).json()
                #print(child_node)
                try:
                    if child_node['parent']['ref'] == fake_wrapper_ao.uri:
                        children_of_fake_wrapper_component_dict[node.uri] = node.position
                except:
                    pass
            
            #Print Dict of Direct Children AOs
            print ("Found " + str(len(children_of_fake_wrapper_component_dict)) + " Direct Children of Wrapper Component")
            row.append(str(len(children_of_fake_wrapper_component_dict)) + " children of Wrapper AO")
            print ("Reposting children as direct children of resource...")

            
            #Capture any error responses and save to output CSV report
            success_ao_keys_list = []
            fail_ao_keys_list = []
            
            for key, value in children_of_fake_wrapper_component_dict.items():
                #Repost AOs as direct children of Resource (to flatten the tree) based on Dict info 
                update_resource = aspace_client.post(resource_object.uri + '/accept_children', params={'children[]': key, 'position': value}).json()
                try:
                    if update_resource['status'] == "Updated":
                        print ("Status: " + update_resource['status'])
                        success_ao_keys_list.append(key)
                    else:
                        print("NOT UPDATED")
                        fail_ao_keys_list.append(key)
                except:
                    print("ERROR REPOSTING AO")
                    fail_ao_keys_list.append(key)
            
            if len(fail_ao_keys_list) != 0:
                row.append("ERROR Posting AOs: " + str(fail_ao_keys_list))
            else:
                row.append("SUCCESS - All AOs reposted")
            
            #Delete the fake wrapper component
            delete_fake_wrapper_ao = aspace_client.delete(fake_wrapper_ao.uri).json()
            print ("Deleting fake wrapper component: " + delete_fake_wrapper_ao["status"])
            row.append("Fake AO Delete Status: " + delete_fake_wrapper_ao["status"])
        
            if_published_export_EAD(resource_object)          
       
        #SKIP IF RESOURCE HAS MORE THAN ONE TOP-LEVEL AO
        else:
            print("Skipping - Collection has MORE THAN 1 top level AO\n")
            row.append("SKIPPING - 2+ top-level AOs")
            
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        iso_timestamp = datetime.fromtimestamp(timestamp)
        row.append(iso_timestamp)
            
        with open(updated_resources_csv,'at') as csvout:
                writer = csv.writer(csvout)
                writer.writerow(row)