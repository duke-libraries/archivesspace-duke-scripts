SELECT 
	resource.identifier as collection_id,
	resource.title as collection_title,
	resource.ead_id,
	note.archival_object_id,
	archival_object.display_string as archival_object_title,
	archival_object.ref_id,
	enumeration_value.value as level,
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
	notes LIKE "%accessrestrict%" 
AND
	archival_object_id IS NOT NULL
ORDER BY resource.identifier