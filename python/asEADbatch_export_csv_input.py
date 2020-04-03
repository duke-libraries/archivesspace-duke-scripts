#Script takes input CSV of ASpace Resource URIs in column 1 (e.g. /repositories/2/resources/1005)
#Then, checks to see if REsources have finding_aid_status = 'published' in ASpace
#If so, exports EADs to specified location using EADID as filename


import io
import csv
from asnake.client import ASnakeClient
from asnake.aspace import ASpace

aspace = ASpace(baseurl="[ASPACE BACKEND URL]",
                      username="[USERNAME]",
                      password="[PASSWORD]")

#Log Into ASpace and set repo to RL
aspace_client = ASnakeClient(baseurl="[ASPACE BACKEND URL]",
                      username="[USERNAME]",
                      password="[PASSWORD]")

aspace_client.authorize()
repo = aspace_client.get("repositories/2").json()
print("Logged into: " + repo['name'])

destination = 'C:/users/nh48/desktop/as_exports_temp/'

input_csv = input("Path to CSV Input: ")
#output will be input CSV plus some extra columns for reporting on actions taken, errors, etc.
updated_records_csv = input("Path to CSV Output: ")


#If Resource finding aid status = published, export the EAD for the resource, save to folder
def if_published_export_EAD(resource_uri):
    resource_json = aspace_client.get(resource_uri).json()
    published_status = resource_json['finding_aid_status']
    id_uri_string = resource_json['uri'].replace("resources","resource_descriptions")
    #set EAD export options: number components and include DAOs
    export_options = '?include_daos=true&numbered_cs=true&include_unpublished=false'
    destination = 'C:/users/nh48/desktop/as_exports_temp/'
    eadid = resource_json['ead_id']
    if published_status == 'published':
        ead = aspace_client.get(id_uri_string + '.xml' + export_options).text
        f = io.open(destination + eadid + '.xml', mode='w', encoding='utf-8')
        f.write(ead)
        f.close()
        print(eadid + " | Exported\n===============================")
        row.append(eadid)
        row.append("Exported")
    else:
        print (eadid + " | NOT Exported - Finding Aid Status NOT PUBLISHED\n++++++++++++++++++++++++++++")
        row.append(eadid)
        row.append("UNPUBLISHED: EAD NOT EXPORTED")


#Open CSV produced by SQL query and start processing
with open(input_csv,'rt', encoding='utf-8') as csvfile, open(updated_records_csv,'wt') as csvout:
    csvin = csv.reader(csvfile)
    #next(csvin, None) #ignore header row
    csvout = csv.writer(csvout)
    
    for row in csvin:

        resource_uri = row[0]
        if_published_export_EAD(resource_uri)
        
        with open(updated_records_csv,'at', newline='') as csvout:
                writer = csv.writer(csvout)
                writer.writerow(row)
        
        