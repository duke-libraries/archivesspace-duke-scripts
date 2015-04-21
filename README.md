# archivesspace-duke-scripts
Various scripts to process ArchivesSpace EAD exports prior to publication.

**EAD_ASpace_export_post-processor.xsl**

Fixes various validation issues with AS EAD exports, most related to namespace conflicts (ns2: vs. xlink:)


**EADrenamer.py**

Python script to batch rename EAD exports based on value of <eadid> element.
