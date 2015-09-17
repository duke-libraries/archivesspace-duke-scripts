# archivesspace-duke-scripts
Various scripts to process ArchivesSpace EAD exports prior to publication.

**EAD_ASpace_export_post-processor.xsl** - Fixes various validation issues with AS EAD exports, most related to namespace conflicts (ns2: vs. xlink:)

**EADrenamer.py** - Python script to batch rename EAD exports based on value of <eadid> element.

**EADrenamer_published_only.py** - Python script to batch rename EAD exports based on value of <eadid> element.  The script will only process EADs where eadheader/@findaidstatus="published".  Files are renamed and moved to the specified source directory

**asEADexport_public.py** - Python script to batch export all EADs from a specified repository where finding_aid_status=published and save those EADs to a specified location using the EADID as the filename. Can configure export parameters (include DAOs, unpublished, etc.). Usernames, passwords, and repository URLs have been removed. Adapted from: https://gist.github.com/helrond/1ef5b5bd47b47bd52f02

**aspace_dig_guide_creator.xsl** - XSLT that extracts metadata and refIDs from ASpace EAD exports and create a digitization guide spreadsheet (TSV) suitable for use by Digital Production Center (DPC) staff. Digital Object IDs and URIs can be added to the spreadsheet during digitization. This script should be modified based on the level of description in a given collection and the metadata available for any given components in a collection. The completed digitization guide can serve as the basis for batch creating Digital Object records in ASpace and linking them as instances to existing Archival Object (component) records using duke_update_archival_object.py

**duke_update_archival_object.py** - Python script that reads TSV file produced from aspace_dig_guide_creator.xsl script (including Digital Object IDs and URIs) and batch creates digital object records in ArchivesSpace and links them as instances to existing Archival Object records based on the archival object's refID value.  This script should be modified to specify input TSV file location and filename/location for output CSV file. It should also be modified if the column position of the Digital Object IDs or URIs changes in the input TSV file.  This script is adapted from: https://github.com/djpillen/bentley_scripts/blob/master/update_archival_object.py
