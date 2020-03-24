SELECT
	group.repo_id,
	group.group_code, 
	group.group_code_norm, 
	group.description, 
	user.id, 
	user.username, 
	user.source, 
	user.email, 
	user.create_time 

FROM 
  user 
    LEFT JOIN
      group_user ON user.id = group_user.user_id
    LEFT JOIN
      `group` ON group_user.group_id = `group`.id;
