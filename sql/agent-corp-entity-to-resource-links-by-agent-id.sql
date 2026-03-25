SELECT 
	linked_agents_rlshp.agent_corporate_entity_id as corporate_entity_id, 
    resource.id as resource_id, 
    resource.ead_id,
    replace(replace(replace(replace(replace(resource.identifier, ',', '.'), '"', ''), ']', ''), '[', ''), '.null', '') as collection_id,
	resource.title as collection_title,
    ev3.value as finding_aid_status,
    ev1.value as role_term,
    ev2.value as relator_term
FROM 
	resource 
    LEFT JOIN
    linked_agents_rlshp ON resource.id=linked_agents_rlshp.resource_id 
    LEFT JOIN 
    enumeration_value ev1 ON linked_agents_rlshp.role_id=ev1.id 
    LEFT JOIN
    enumeration_value ev2 ON linked_agents_rlshp.relator_id=ev2.id
    LEFT JOIN
    enumeration_value ev3 ON resource.finding_aid_status_id=ev3.id
WHERE 
	resource.repo_id=2 
	AND
    resource.suppressed=0
    AND
    #un-comment desired agent statement:
	linked_agents_rlshp.agent_corporate_entity_id=4788 #(Sallie Bingham Center)
	#linked_agents_rlshp.agent_corporate_entity_id=5087 #(Economists' Papers Archive)
	#linked_agents_rlshp.agent_corporate_entity_id=606 #(John W. Hartman Center)
	#linked_agents_rlshp.agent_corporate_entity_id=686 #(John Hope Franklin Research Center)
	#linked_agents_rlshp.agent_corporate_entity_id=489 #(Archive of Documentary Arts)
	#linked_agents_rlshp.agent_corporate_entity_id=1026 #(Human Rights Archive)
	#linked_agents_rlshp.agent_corporate_entity_id=4641 #(History of Medicine Collection)
	#linked_agents_rlshp.agent_corporate_entity_id=4307 #(University Archives)