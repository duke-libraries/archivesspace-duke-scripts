SELECT 
	agent_person.id as agent_person_id,
    name_person.sort_name as sort_name,
    agent_person.created_by as agent_person_created_by,
    linked_agents_rlshp.agent_person_id as linked_agents_person_id,
    user.username as username
	
FROM 
	agent_person

LEFT JOIN
	linked_agents_rlshp on agent_person.id = linked_agents_rlshp.agent_person_id

LEFT JOIN
	name_person on agent_person.id = name_person.agent_person_id
    
LEFT JOIN
	user on agent_person.id = user.agent_record_id
    
WHERE
	linked_agents_rlshp.agent_person_id is null
    and
    username is null