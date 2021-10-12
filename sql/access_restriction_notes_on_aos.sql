SELECT 
	archival_object.repo_id as repo_id,
    	resource.id as resource_id,
	resource.title as collection_title,
	resource.ead_id as ead_id,
	note.archival_object_id as ao_id,
	/*CREATE url to link directly to AO*/
	CONCAT('https://archivesspace-staff.lib.duke.edu/resources/',resource.id,'/edit#tree::archival_object_',archival_object.id) as link_to_ao,
	archival_object.display_string as archival_object_title,
	archival_object.ref_id as ao_ref_id,
	enumeration_value.value as ao_level,
	/*output full JSON Blob*/
	REPLACE(REPLACE(CONVERT(note.notes using 'utf8'),CHAR(13),''), CHAR(10), '') as note_content,
	note_persistent_id.persistent_id as note_persistent_id

FROM 
	note
		LEFT JOIN
	archival_object on note.archival_object_id = archival_object.id
		LEFT JOIN
	resource on archival_object.root_record_id = resource.id
		LEFT JOIN
	enumeration_value on archival_object.level_id = enumeration_value.id
		LEFT JOIN
	note_persistent_id on note.id = note_persistent_id.note_id

WHERE 
	note.notes LIKE "%accessrestrict%" AND
	/*Include keywords for searching note text below (e.g. dates for expiring restrictions, etc)*/
	(note.notes LIKE "% 2020%" OR note.notes LIKE "% 2021%")
AND
	archival_object_id IS NOT NULL
ORDER BY resource.identifier
