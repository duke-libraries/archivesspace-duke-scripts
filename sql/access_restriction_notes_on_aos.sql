SELECT 
	resource.identifier as collection_id,
	resource.title as collection_title,
	resource.ead_id,
	note.archival_object_id,
	/*CREATE url to link directly to AO*/
	CONCAT('https://archivesspace-staff.lib.duke.edu/resources/',resource.id,'/edit#tree::archival_object_',archival_object.id) as link_to_ao,
	archival_object.display_string as archival_object_title,
	archival_object.ref_id,
	enumeration_value.value as level,
	/*output full JSON Blob*/
	CONVERT(note.notes USING utf8) as note_content,
	note.id as note_identifier

FROM 
	note
		LEFT JOIN
	archival_object on note.archival_object_id = archival_object.id
		LEFT JOIN
	resource on archival_object.root_record_id = resource.id
		LEFT JOIN
	enumeration_value on archival_object.level_id = enumeration_value.id

WHERE 
	note.notes LIKE "%accessrestrict%" AND
	/*Include keywords for searching note text below (e.g. dates for expiring restrictions, etc)*/
	note.notes LIKE "% 2020%"
AND
	archival_object_id IS NOT NULL
ORDER BY resource.identifier