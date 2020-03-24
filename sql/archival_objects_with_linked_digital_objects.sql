SELECT

archival_object.id as archival_object_uri_id,
archival_object.title,
archival_object.ref_id,
digital_object.id as digital_object_uri_id,
digital_object.title,
digital_object.digital_object_id


FROM `archival_object`
left join instance on archival_object.id = instance.archival_object_id
left join instance_do_link_rlshp on instance.id = instance_do_link_rlshp.instance_id
left join digital_object on instance_do_link_rlshp.digital_object_id = digital_object.id

/* search for string in AO refID */
where archival_object.ref_id like '%seca-%'
