# archivesspace-duke-scripts
Various scripts to process ArchivesSpace EAD exports prior to publication.

**EAD_ASpace_export_post-processor.xsl** - Fixes various validation issues with AS EAD exports, most related to namespace conflicts (ns2: vs. xlink:)

**EADrenamer.py** - Python script to batch rename EAD exports based on value of <eadid> element.

**EADrenamer_published_only.py** - Python script to batch rename EAD exports based on value of <eadid> element.  The script will only process EADs where eadheader/@findaidstatus="published".  Files are renamed and moved to the specified source directory

**asEADexport_public.py** - Python script to batch export all EADs from a specified repository where finding_aid_status=published and save those EADs to a specified location using the EADID as the filename. Can configure export parameters (include DAOs, unpublished, etc.). Usernames, passwords, and repository URLs have been removed. Adapted from: https://gist.github.com/helrond/1ef5b5bd47b47bd52f02
