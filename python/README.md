# Accessions
**duke_update_accessions.py** - Script currently updates a single field in accession records, can be modified to target specific fields. Takes CSV input where column 1 contains the Accession's ASpace ID (from the URI) and column 2 contains the values to update. CSV should not include a header row.

# Agents / Subjects
**duke_publish_agents.py** - Python script that publishes all agent records of all types and outputs log to txt file.

# Archival Objects
**as-batch-delete-archival-objects.py** - Python script that batch deletes archival objects using an input CSV where the first column contains archival object IDs (the ID in the URI). The CSV should not include a header row. Lists of archival object IDs can be obtained by searching in the backend SQL database, then exporting as CSV.

**duke_update_archival_object.py** - Python script that reads CSV file containing ArchivesSpace archival object ref_IDs, digital object identifiers, URLs, and file_version_use_statements and batch creates digital object records and links them as instances to existing archival object records based on the archival object's refID value. Script also outputs a CSV file including all the info in the input CSV and the URIs of the created digital objects and updated archival object records.  The script prompts for the ASpace backend URL, login credentials, location of input and output CSV, and whether or not the created digital objects should be published.
This script is adapted from: https://github.com/djpillen/bentley_scripts/blob/master/update_archival_object.py

**duke_update_archival_object_args.py** - Python script that reads TSV file produces from aspace_dig_guide_creator.xsl script and batch loads digital object records in ArchivesSpace and links them as instances to existing archival object component records based on the archival object's refID value. In other words, it functions similarly to duke_update_archival_object.py. It differs in that it accepts arguments for the input TSV file and output CSV file, as well as arguments for the Aspace User ID and password. It also will read file version use statements from the input TSV. It still must be modified to map the correct column position of the Digital Object IDs, URIs, and File Version Use Statements. This script was adapated from duke_update_archival_object.py which was itself adapted from: https://github.com/djpillen/bentley_scripts/blob/master/update_archival_object.py

**as_change_ao_level.py** - Python script that takes 2-column input CSV (AO ID, desired_level) and updates level of description values in ASpace accordingly, writing log to output CSV.

**duke_archival_object_metadata_adder.py** - Script currently adds a repository processing note based on two column CSV input file where column 1 contains the archival object ref_id and column 2 contains the text of the note to add. Could be modified to target other fields.

**duke_update_ao_titles_and_dates.py** - Script updates archival object titles and dates using three column CSV input file where column 1 contains the AO ref_id, column 2 contains the updated Title, column 3 (optional) contains updated date expressions.

# Containers
**duke_update_archival_object_containers.py** - Python script that batch updates archival objects with new top containers. Input is a CSV with three columns: Archival Object URI, old top container URI, and new top container URI.

# Digital Objects
**asUpdateDAOs.py** - A python script used to update Digital Object identifiers and file version URIs in ASpace based on an input CSV with refIDs for the the linked Archival Object.  Input is a five column CSV (without column headers) that includes: #[old file version use statement],[old file version URI],[new file version URI],[ASpace ref_id],[ark identifier in DDR (e.g. ark:/87924/r34j0b091)].

**duke_create_ao_and_do.py** - ONLY WORKS WITH ARCHIVESSPACE v.1.5+. Starting with an input CSV, this script will use the ArchivesSpace API to batch create archival object records in ASpace as children of a specified archival object parent (e.g. a series/subseries/file). The script will then create digital object records from the same input CSV and link them as instances of the newly created archival objects. Finally, the script will output a CSV containing all of the info in the input CSV plus the refIDs and URIs for the created archival objects and the URIs for the created digital objects.

**as-batch-delete-digital-objects-by-identifier.py** - Python script that batch deletes digital objects based on CSV input where column one contains Digital Object Identifiers. Digital object IDs can be obtained from a repository export (typically ARKs) or by searching in the AS backend SQL database and exporting records as CSV. Script uses find_by_id/digital_objects endpoint. Only available in 2.1?

**as-batch-delete-digital-objects.py** - Python script that batch deletes digital objects based on CSV input where column one contains ASpace digital object IDs (the ID in the URI). The CSV should not have a header row. IDs can be obtained by querying the ASpace backend SQL database and exporting results as CSV.

**as-batch-publish-unpublish-dos-by-identifier.py** - Script currently takes a CSV as input (with digital object identifier in first column) and publishes or unpublishes the DO--as specified in script on line 64. Identifiers are typically ARKs and can be obtained through a repository export or by querying ASpace backend SQL database and exporting results as CSV.

# EAD Stuff
**EADrenamer.py** - Python script to batch rename EAD exports based on value of `<eadid>` element.

**EADrenamer_published_only.py** - Python script to batch rename EAD exports based on value of `<eadid>` element.  The script will only process EADs where eadheader/@findaidstatus="published".  Files are renamed and moved to the specified source directory

**asEADexport_public.py** - Python script to batch export all EADs from a specified repository where finding_aid_status=published and save those EADs to a specified location using the `<eadid>` value as the filename. Can configure export parameters (include DAOs, unpublished, etc.). Usernames, passwords, and repository URLs have been removed. Adapted from: https://gist.github.com/helrond/1ef5b5bd47b47bd52f02

**asEADexport_eadid_input.py** - Python script to batch export EADs based on eadid input. Prompts for a list of eadid values separated with commas (e.g. eadid1,eadid2,eadid3). Will export EADs for all eadids provided if marked "published" in ASpace. Script requires a config file (local_settings.cfg) in the same directory that contains the backend URL, username, password.

Example of local_settings.cfg:
```
[ArchivesSpace]
baseURL:http://aspace-backend-url.lib.duke.edu
repository:1
user:admin
password:adminpassword
```

**asEADpublish_and_export_eadid_input.py** - Python script (similar to above) that exports EADs based on eadid input. Prompts for list of eadid values separated with commas. Checks to see if a resource's finding aid status is 'published'.  If so, it exports the EAD to a specified location, if not, it sets the finding aid status to "published" AND publishes the resource and all components.  Then, it exports the modified EAD.  See comments in script for more details.

**asEADpublish_and_export_rlid_input.py** - Python script (similar to above) that exports EADs based on collection number input. Prompts for list of collection number values separated with commas (e.g. rl-01234, rl-01243). Checks to see if a resource's finding aid status is 'published'. If so, it exports the EAD to a specified location, if not, it sets the finding aid status to "published" AND publishes the resource and all components. Then, it exports the modified EAD.  See comments in script for more details.

**nlm_sitemap_generator.py** - Python script used to generate Sitemap for contributing EADs to: https://www.nlm.nih.gov/hmd/consortium/index.html. Script searches for terms 'medicine' and 'physician' in text of //controlaccess//text() for EAD files in input directory and generates sitemap of finding aid URLs and lastmod times for matching finding aids.

# Notes
**duke_as_replace_notes.py** - Python script that reads CSV, finds notes, and replaces existing note text with new text provided in CSV. Primarily used to clean up accessrestrict notes. Script slightly modified from script provided by Alicia Detelich (Yale Manuscripts and Archives)

**duke_as_replace_notes_restrictions.py** - Python script that reads CSV, finds restriction notes, and replaces note text while supplying a local access restriction type and a restriction end date from the input CSV.

# Other Stuff
**as-batch-delete-by-uri.py** - Python script currently takes a CSV as input (with Aspace URI as first column--e.g. https://aspace.library.edu/repositories/2/archival_objects/1234) and deletes the record. Script also outputs separate CSV with copy of input CSV and an added column for delete status.
