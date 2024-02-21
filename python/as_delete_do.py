#!/usr/bin/env python3.11

"""This file reads a CSV and then makes API calls to delete the DOs in AS
Requires a CSV file with the DO IDs in the first column
Requires a config file with the AS API URL, username, password, and repository ID"""

import csv
import requests
import sys
import configparser
import logging

# CONSTANTS
CSV_FILE = 'DOs.csv'
CONFIG_FILE = 'asnake_local_settings.cfg'

configFilePath = CONFIG_FILE
config = configparser.ConfigParser()
config.read(configFilePath)

logging.basicConfig(filename='AS_delete_DO.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

AS_usernamne = config.get('ArchivesSpace', 'user')
AS_api_url = config.get('ArchivesSpace', 'baseURL')
AS_repository_id = config.get('ArchivesSpace', 'repository')
AS_password = config.get('ArchivesSpace', 'password')

logging.info(f'AS_usernamne: {AS_usernamne}')
logging.info(f'AS_api_url: {AS_api_url}')
logging.info(f'AS_repository_id: {AS_repository_id}')
logging.info(f'CSV_FILE: {CSV_FILE}')

with open(CSV_FILE, 'r') as f:
    reader = csv.reader(f)
    DOs = list(reader)

input(f'About to delete {len(DOs)} DOs. Press Enter to continue or Ctrl+C to quit.')

for i in DOs:
    print(f'URL: {AS_api_url}/repositories/{AS_repository_id}/digital_objects/{i[0]}')
    logging.info(f'URL: {AS_api_url}/repositories/{AS_repository_id}/digital_objects/{i[0]}')
    # Delete the # in the next line to actually delete the DOs
    response = requests.delete(f'{AS_api_url}/repositories/{AS_repository_id}/digital_objects/{i[0]}', auth=(AS_usernamne, AS_password))
    logging.info(f'Response: {response.status_code} - {response.text}')
