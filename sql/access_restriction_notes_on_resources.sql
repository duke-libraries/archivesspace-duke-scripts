SELECT 
	resource.id as resource_URI,
	resource.identifier as collection_id,
	resource.title as collection_title,
	resource.ead_id,
	note.id as note_identifier,
	note_persistent_id.persistent_id as note_PID,
	CONVERT(note.notes USING utf8) as note_content

FROM 
	note
		LEFT JOIN
	resource on note.resource_id = resource.id
		LEFT JOIN
	note_persistent_id on note.id = note_persistent_id.note_id

WHERE 
	note.notes LIKE "%accessrestrict%" 
AND
	note.resource_id IS NOT NULL
ORDER BY resource.identifier