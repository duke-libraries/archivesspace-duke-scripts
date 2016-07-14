# archivesspace-duke-scripts
Various scripts to process ArchivesSpace EAD exports, interact with the ArchivesSpace API, or query backend ASpace SQL database for reports

**EADrenamer.py** - Python script to batch rename EAD exports based on value of <eadid> element.

**EADrenamer_published_only.py** - Python script to batch rename EAD exports based on value of <eadid> element.  The script will only process EADs where eadheader/@findaidstatus="published".  Files are renamed and moved to the specified source directory

**asEADexport_public.py** - Python script to batch export all EADs from a specified repository where finding_aid_status=published and save those EADs to a specified location using the <eadid> value as the filename. Can configure export parameters (include DAOs, unpublished, etc.). Usernames, passwords, and repository URLs have been removed. Adapted from: https://gist.github.com/helrond/1ef5b5bd47b47bd52f02

**asEADexport_eadid_input.py** - Python script to batch export EADs based on eadid input. Prompts for a list of eadid values separated with commas (e.g. eadid1,eadid2,eadid3). Will export EADs for all eadids provided if marked "published" in ASpace. Script relies on a config file (local_settings.cfg) that contains repository URL, username, password.

For example:
```
[ArchivesSpace]
baseURL:http://aspace-backend-url.lib.duke.edu
repository:1
user:admin
password:adminpassword
```

**duke_update_archival_object.py** - Python script that reads TSV file produced from aspace_dig_guide_creator.xsl script (including Digital Object IDs and URIs) and batch loads digital object records in ArchivesSpace and links them as instances to existing archival object component records based on the archival object's refID value. This script should be modified to specify input TSV file location and filename/location for output CSV file. It should also be modified if the column position of the Digital Object IDs or URIs changes in the input TSV file.  This script is adapted from: https://github.com/djpillen/bentley_scripts/blob/master/update_archival_object.py

**duke_update_archival_object_args.py** - Python script that reads TSV file produces from aspace_dig_guide_creator.xsl script and batch loads digital object records in ArchivesSpace and links them as instances to existing archival object component records based on the archival object's refID value. In other words, it functions similarly to duke_update_archival_object.py. It differs in that it accepts arguments for the input TSV file and output CSV file, as well as arguments for the Aspace User ID and password. It also will read file version use statements from the input TSV. It still must be modified to map the correct column position of the Digital Object IDs, URIs, and File Version Use Statements. This script was adapated from duke_update_archival_object.py which was itself adapted from: https://github.com/djpillen/bentley_scripts/blob/master/update_archival_object.py

