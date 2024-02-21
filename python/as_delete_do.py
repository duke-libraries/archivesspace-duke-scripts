#!/usr/bin/env python3.11

"""This file reads a CSV and then makes API calls to delete the DOs in AS
Requires a CSV file with the DO IDs in the first column
Requires a config file with the AS API URL, username, password, and repository ID"""

import csv
import requests
import sys
import configparser
import logging

DEBUG = True

# CONSTANTS
CSV_FILE = 'DOs.csv'
CONFIG_FILE = 'asnake_local_settings.cfg'

configFilePath = CONFIG_FILE
config = configparser.ConfigParser()
config.read(configFilePath)

logging.basicConfig(filename='AS_delete_DO.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

AS_username = config.get('ArchivesSpace', 'user')
AS_api_url = config.get('ArchivesSpace', 'baseURL')
AS_repository_id = config.get('ArchivesSpace', 'repository')
AS_password = config.get('ArchivesSpace', 'password')

logging.info(f'AS_username: {AS_username}')
logging.info(f'AS_api_url: {AS_api_url}')
logging.info(f'AS_repository_id: {AS_repository_id}')
logging.info(f'CSV_FILE: {CSV_FILE}')

# Session Authentication
auth = requests.post(AS_api_url + '/users/' + AS_username+ '/login?password='
                     + AS_password)
if auth.status_code == 200:
    auth_json = auth.json()
    if DEBUG:
        print("DEBUG======================DEBUG")
        print(f'Response text: \n {auth_json}')
        print("DEBUG======================DEBUG")
    print('Login successful! Continuing process.')
else:
    print(f'Login failed! Response text: \n {auth.text}')
    print('Exiting process.')
    exit()

session = auth_json['session']
headers = {'X-ArchivesSpace-Session': session,
           'Content_Type': 'application/json'}

with open(CSV_FILE, 'r') as f:
    reader = csv.reader(f)
    DOs = list(reader)

input(f'About to delete {len(DOs)} DOs. Press Enter to continue or Ctrl+C to quit.')

for i in DOs:
    print(f'URL: {AS_api_url}/repositories/{AS_repository_id}/digital_objects/{i[0]}')
    logging.info(f'URL: {AS_api_url}/repositories/{AS_repository_id}/digital_objects/{i[0]}')
    # Delete the # in the next line to actually delete the DOs
    response = requests.delete(f'{AS_api_url}/repositories/{AS_repository_id}/digital_objects/{i[0]}', headers = headers, auth=(AS_username, AS_password))
    logging.info(f'Response: {response.status_code} - {response.text}')
