SELECT 
	resource.id as resource_id,
    resource.ead_id as ead_id,
	resource.title as collection_title,
    ev2.value as finding_aid_status,
	note.archival_object_id as ao_id,
	/* Include following line to CREATE url to link directly to archival object in ArchivesSpace */
	/* CONCAT('https://archivesspace-staff.lib.duke.edu/resources/',resource.id,'/edit#tree::archival_object_',archival_object.id) as link_to_ao, */
	archival_object.display_string as archival_object_title,
	archival_object.ref_id as ao_ref_id,
	ev1.value as ao_level,
	json_extract(convert(note.notes using utf8), '$.rights_restriction[0].local_access_restriction_type') as local_access_restrict_type,
    /* include following line for full JSON blob */
    /* REPLACE(REPLACE(CONVERT(note.notes using 'utf8'),CHAR(13),''), CHAR(10), '') as note_content, */
	json_extract(convert(note.notes using utf8), '$.subnotes[0].content') as note_content_text,
	note_persistent_id.persistent_id as note_persistent_id

FROM 
	note
		LEFT JOIN
	archival_object on note.archival_object_id = archival_object.id
		LEFT JOIN
	resource on archival_object.root_record_id = resource.id
		LEFT JOIN
	enumeration_value ev1 on archival_object.level_id = ev1.id
		LEFT JOIN
	enumeration_value ev2 on resource.finding_aid_status_id=ev2.id
        left join 
	note_persistent_id on note.id = note_persistent_id.note_id

WHERE 
	resource.repo_id=2 
		AND
	resource.suppressed=0
		AND
    note.notes LIKE "%accessrestrict%"
    /* Include following line and edit to use keywords, exact phrases, etc. for searching note text (e.g. dates for expiring restrictions, etc)*/
	/*AND (note.notes LIKE "% 2020%" OR note.notes LIKE "% 2021%")*/
		AND
	archival_object_id IS NOT NULL
ORDER BY resource.identifier
