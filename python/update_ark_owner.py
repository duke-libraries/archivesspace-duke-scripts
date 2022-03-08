import requests
import configparser
import csv

#Script takes two-column CSV input and transfers ownership of ARKs in EZID from one EZID user to another
#Specifically used to move ArcLight ARKs from 'duke_ddr' owner to 'duke_rl' owner

#ASpace credentials and other variables stored in local config file
configFilePath = 'asnake_local_settings.cfg'
config = configparser.ConfigParser()
config.read(configFilePath)

EZID_username = config.get('EZID', 'ezid_username')
EZID_password = config.get('EZID', 'ezid_password')
ARK_shoulder = config.get('EZID', 'ark_shoulder')
ARK_owner = config.get('EZID', 'ark_owner')

#For Single item testing
#ARK_id = 'ark:/87924/m1159q'

#Input is two column CSV with EADID and Finding Aid location field as exported from ASpace (e.g. https://idn.duke.edu/ark:/87924/m1001n)
input_csv = input("Path to Input CSV: ")
output_csv = input("Path to Output CSV: ")

#Update ARK Function
def update_ark_owner(ARK_id):
     
    #Set ArcLight owner to 'duke_rl' (previously duke_ddr)
    new_ark_owner = '_owner: duke_rl'
    
    #EZID seems to need these headers to be explicit
    headers = {'Content-type': 'text/plain; charset=UTF-8'}
    
    print ('Updating ARK...')
    
    try: 
        update_ark = requests.post('https://ezid.cdlib.org/id/{0}'.format(ARK_id), headers=headers, data=new_ark_owner, auth=(EZID_username, EZID_password))
        
        #responses look like (success: ark:/99999/fk4jm3mb69)
        response_text = update_ark.text
        
        #convert response to a Dict (e.g. {'success': 'ark:/99999/fdkl;jlkj'})
        response_dict = dict(response_text.split(': ',1) for line in response_text.strip().split('\n'))
        
        #print (mint_response_dict['success'])
        updated_ark = response_dict['success']
        #print (minted_ark)
        
        #get metadata about the ARK you just minted...
        get_updated_ark = requests.get('https://ezid.cdlib.org/id/{0}'.format(updated_ark), auth=(EZID_username, EZID_password))
        print (get_updated_ark.text)
        
        #Prepend Duke URL stuff to beginning of ARK
        full_ark_uri = "https://idn.duke.edu/{0}".format(updated_ark)
        #print (full_ark_uri)
        
        row['ezid_update_response'] = get_updated_ark.text
        row['full_uri'] = full_ark_uri
         
    except:
        print ('ERROR UPDATING ARK: ' + ARK_id)
        
with open(input_csv,'rt', newline='', encoding='utf-8') as csvfile, open(output_csv,'wt', newline='', encoding='utf-8') as csvout:
    csvin = csv.DictReader(csvfile) #DictReader allows accessing columns by header name and not row index
    fieldnames = csvin.fieldnames + ['ezid_update_response'] + ['full_uri']
    writer_csv = csv.DictWriter(csvout, fieldnames, delimiter=",")
    writer_csv.writeheader()

    for i, row in enumerate(csvin):
        
        if(i >+ 5000): #Testing with first # rows
            break
        
        ead_location = row['ead_location']
        eadid = row['ead_id']
    
        #Grab ARK string from full ead_location field (e.g. https://idn.duke.edu/ark:/87924/m1001n)
        ARK_id = ead_location.replace('https://idn.duke.edu/','')
        
        print (ARK_id)
        
        update_ark_owner(ARK_id)
        
        #Write output CSV row
        writer_csv.writerow(row)
        
        
        