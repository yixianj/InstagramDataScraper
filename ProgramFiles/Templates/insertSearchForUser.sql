UPDATE ig_users
SET search = search || '{
{{searchId}}
}'
WHERE id = {{id}};