#Python3.7
import io
import json
import time

from asnake.client import ASnakeClient
from asnake.aspace import ASpace

#BaseURL should point to backend (e.g. https://archivesspace.duke.edu/api or https://localhost:8089)
aspace = ASpace(baseurl="[baseurl]",
                      username="[username]",
                      password="[password]")

#Log Into ASpace and set repo to RL
aspace_client = ASnakeClient(baseurl="[baseurl]",
                      username="[username]",
                      password="[password]")
aspace_client.authorize()

#set target repo by id
repo = aspace_client.get("repositories/2").json()
print("Logged into: " + repo['name'])


# Prompt for input, a comma separated list of EADID values (e.g. johndoepapers, janedoepapers, johnandjanedoepapers)
eadids = input("List of EADIDs:  ")
# Split comma separated list
eadids_list = eadids.split(",")

destination = 'C:/users/nh48/desktop/as_exports_temp/'

#set EAD export options: number components and include DAOs
export_options = '?include_daos=true&numbered_cs=true&include_unpublished=false'


#Check if any unpublished nodes in the resource tree and if so, do not publish and export
def has_unpublished_nodes():
    print(eadID + " | checking for any unpublished children in the tree...")
    rl_repo = aspace.repositories(2)
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

#iterate over EADIDs in input list
for eadid in eadids_list:
    
#advanced search for EADID    
    results = aspace_client.get('repositories/2/search?page=1&aq={\"query\":{\"field\":\"ead_id\",\"value\":\"'+eadid+'\",\"jsonmodel_type\":\"field_query\",\"negated\":false,\"literal\":false}}').json()

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

#If the resource has a repository processing note, print it out to console. 
#Confirm that you want to proceed with publishing
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

#Test for unpublished nodes, only proceed with publish and export if no unpublished nodes
        if has_unpublished_nodes() == False:

#If the finding aid status is already set to publish, just export the EAD
            if "published" in publish_status:
            # Set publish to 'true' for all levels, components, notes, etc.  Same as clicking "publish all" in staff UI
                resource_publish_all = aspace_client.post(resource_uri + '/publish')
                print (eadID + ' | resource and all children set to published')
            #Pause for 10 seconds so publish action takes effect...maybe?
                print (eadid + " | Pausing for 10 seconds to index publish action...")
                time.sleep(10.0)
                print (eadID + " | Exporting EAD file...")
                ead = aspace_client.get(id_uri_string + '.xml' + export_options).text
                f = io.open(destination+eadID+'.xml', mode='w', encoding='utf-8')
                f.write(ead)
                f.close()
                print (eadID + '.xml' ' | ' + resource_id + ' | ' + aspace_id_short + ' | ' + last_modified_by + ' | ' + user_mtime_slice + ' | ' + 'exported')
    
    #If not published, set finding aid status to published
            else:
                print (eadID + " | Finding aid status: " + publish_status)
                resource_publish_all = aspace_client.post(resource_uri + '/publish')
                print (eadID + ' | resource and all children set to published')
                print (eadID + " | Pausing for 10 seconds to index publish action...")
                time.sleep(10.0)
                resource_json['finding_aid_status'] = 'published'
                resource_data = json.dumps(resource_json)
                #Repost the Resource with the published status
                resource_update = aspace_client.post(resource_uri, json=resource_data).json()
                print (eadID + ' | reposted resource with finding aid status = published')
            #Pause for 10 seconds so publish action takes effect
                print (eadID + " | Pausing for 10 seconds to index reposted resource...")
                time.sleep(10.0)
                print (eadID + " | Exporting EAD file...")
                
                #export EAD file
                ead = aspace_client.get(id_uri_string + '.xml' + export_options).text
                
                #write exported EAD to local directory using EADID as filename
                f = io.open(destination + eadID + '.xml', mode='w', encoding='utf-8')
                f.write(ead)
                f.close()
                print (eadID + '.xml' ' | ' + resource_id + ' | ' + aspace_id_short + ' | ' + last_modified_by + ' | ' + user_mtime_slice + ' | ' + 'exported')

        else:
            print(eadID + " | STOPPING - please review unpublished nodes in " + eadID)
    else:
        print (eadID + ' | ***ERROR***: ' + eadid + ' does not exist!')

input("All done!. Press Enter to Exit")