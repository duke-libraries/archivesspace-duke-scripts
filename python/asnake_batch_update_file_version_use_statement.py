# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 15:02:09 2019

@author: nh48
"""
#first column of input CSV should contain URIs of Digital Objects
#URIs take the form (e.g. /repositories/2/digital_objects/1234)
#Script will prompt for input CSV, output CSV and desired file_version_use_statement value
#Then it will update all use statement values to the input value and set all DOs and file_versions to published

import csv
from asnake.client import ASnakeClient
from asnake.aspace import ASpace

aspace = ASpace(baseurl="[API URL]",
                      username="[USERNAME]",
                      password="[PASSWORD]")

#Log Into ASpace and set repo to RL
aspace_client = ASnakeClient(baseurl="[API URL]",
                      username="[USERNAME]",
                      password="[PASSWORD]")

aspace_client.authorize()

repo = aspace_client.get("repositories/2").json()
print("Logged into: " + repo['name'])

input_csv = input("Path to CSV Input: ")
output_csv = input("Path to Output CSV: ")

#publish_boolean = input("Publish? Type True or False: ")

new_use_statement_value = input("New Use Statement Value (e.g. web-archive): ")

with open(input_csv,'rt') as csvfile, open(output_csv,'wt') as csvout:
    reader = csv.reader(csvfile)
    next(csvfile, None) #ignore header row
    csvout = csv.writer(csvout)
    
    for row in reader:
        object_uri = row[0]
        object_json = aspace_client.get(object_uri).json()
        print(object_json['title'])
        object_json['publish'] = True
        
        try:
            for file_version in object_json['file_versions']:
                #print (file_version['use_statement'])
                #row.append("Old File Version: " + file_version['use_statement'])
                file_version['use_statement'] = 'web-archive'
                file_version['publish'] = True
        
        except:
            print("Skipping - no file versions")
            row.append('NO CHANGES')
        
        record_update = aspace_client.post(object_uri, json=object_json).json()
        row.append(record_update)
        print (record_update)
                    
        with open(output_csv,'at') as csvout:
            writer = csv.writer(csvout)
            writer.writerow(row)
