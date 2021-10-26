#/usr/bin/python3
#~/anaconda3/bin/python
from asnake.aspace import ASpace
from asnake.client import ASnakeClient

#Used to fix cases where date expression contains Timestamp info (probably an Excel problem)
#Can perform any string find/replace action on date expression

#Production
aspace = ASpace(baseurl="[api url]",
                username="[username]",
                password="[password]")

#Log Into ASpace and set repo to RL
aspace_client = ASnakeClient(baseurl="[api_url]",
                      username="[username]",
                      password="[password]")


aspace_client.authorize()

repo_id = input("Repository ID")
resource_id = input("Resource_ID: ")
search_string = input("Search String: ")
replace_string = input("Replace String: ")

def date_expression_update(resource_id):
    rl_repo = aspace.repositories(repo_id)
    resource_record = rl_repo.resources(resource_id).tree
    resource_tree = resource_record.walk
    
    for node in resource_tree:
    
        ao_json = aspace_client.get(node.uri).json()   
        
        for date in ao_json['dates']:
            try:
                if search_string in date['expression']:
                    print ("Found: " + date['expression'])
                    date['expression'] = date['expression'].replace(search_string, replace_string)
                    print ("Replaced " + search_string + " with " + replace_string)
                    record_update = aspace_client.post(node.uri, json=ao_json).json()
                else:
                    record_update = "No Matching String in Date Subrecord"
                    pass
                
                print (record_update)
                    
            except:
                print ("No Date Subrecord for this AO")
    
#Put resource record ID here
date_expression_update(resource_id)