SELECT 
	CONCAT("/repositories/2/digital_objects/", digital_object.id) as digital_object_uri,
    digital_object.digital_object_id,
    file_version.file_uri,
    digital_object.title,
    digital_object.created_by,
    digital_object.create_time,
    instance_do_link_rlshp.digital_object_id as linked_rlshp,
    instance_do_link_rlshp.instance_id as linked_instance_id

FROM 
	digital_object

LEFT JOIN 
	instance_do_link_rlshp on digital_object.id = instance_do_link_rlshp.digital_object_id

LEFT JOIN
	file_version on digital_object.id = file_version.digital_object_id
    
WHERE
	instance_do_link_rlshp.digital_object_id is NULL