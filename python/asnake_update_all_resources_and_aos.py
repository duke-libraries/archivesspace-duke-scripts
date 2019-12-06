#/usr/bin/python3
#~/anaconda3/bin/python
from asnake.client import ASnakeClient
import asnake.logging as logging

logging.setup_logging(filename="date_update.log",filemode="a")
logger = logging.get_logger("date_updating")

#Log Into ASpace and set repo to RL
aspace_client = ASnakeClient(baseurl="[backendURL]",
                      username="[USERNAME]",
                      password="[PASSWORD]")
aspace_client.authorize()
repo = aspace_client.get("repositories/2").json()
print("Logged into: " + repo['name'])

print("Getting list of resources...")
resources_list = aspace_client.get("repositories/2/resources?all_ids=true").json()
resources_sorted = sorted(resources_list, reverse=True)

for resource in resources_sorted:

    try:
        resource_json = aspace_client.get("repositories/2/resources/" + str(resource)).json()
        #print (resource_json)
        resource_uri = resource_json['uri']
        print ("updating: " + resource_uri)
        resource_update = aspace_client.post(resource_json['uri'], json=resource_json)
        response = resource_update.json()
        logger.info('update_resource', action='updating-resource', data={'resource_uri': resource_uri, 'response': response})
        print (response['status'])
    except:
        print("ERROR")
        pass
print("All Done with Resources...")

print("Getting list of archival_objects...")
ao_list = aspace_client.get("repositories/2/archival_objects?all_ids=true").json()
ao_list_sorted = sorted(ao_list, reverse=True)

for ao in ao_list_sorted:
    try:
        ao_json = aspace_client.get("repositories/2/archival_objects/" + str(ao)).json()
        #print (ao_json)
        ao_uri = ao_json['uri']
        print ("updating: " + ao_uri)
        ao_update = aspace_client.post(ao_json['uri'], json=ao_json)
        response = ao_update.json()
        logger.info('update_ao', action='updating-ao', data={'ao_uri': ao_uri, 'response': response})
        print (response['status'])
    except:
        print ("ERROR")
        pass
   
print("All Done with Archival Objects...")