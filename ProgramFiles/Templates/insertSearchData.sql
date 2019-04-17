INSERT INTO search_data (
googleCSE, search, search_date, io
)
SELECT * FROM json_to_record($${
"googleCSE": {{googleCSE}},
"search": {{search}},
"date": "{{date}}",
"io": {{io}}
}$$)
AS (
googleCSE json,
search json,
date timestamptz,
io json
)
RETURNING id;