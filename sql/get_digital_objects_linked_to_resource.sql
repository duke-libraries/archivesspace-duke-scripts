SELECT

resource.id as resource_id,
resource.title as resource_title,
archival_object.id as archival_object_uri_id,
archival_object.title,
archival_object.ref_id,
digital_object.id as digital_object_uri_id,
digital_object.title,
digital_object.digital_object_id


FROM `archival_object`
join resource on archival_object.root_record_id = resource.id
join instance on archival_object.id = instance.archival_object_id
join instance_do_link_rlshp on instance.id = instance_do_link_rlshp.instance_id
join digital_object on instance_do_link_rlshp.digital_object_id = digital_object.id

/*insert ASpace Resource Record ID below to scope search to DOs attached to specified resource*/
where archival_object.root_record_id = 3837