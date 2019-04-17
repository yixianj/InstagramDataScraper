INSERT INTO post_data(
{%- for key, value in postData.items() -%}
    {{key}}
    {%- if loop.last == false -%}
        ,
    {%- endif -%}
{%- endfor -%}
)
SELECT * FROM json_to_record($${
{% for key, value in postData.items() -%}
    "{{key}}":
    {%- if key == "edge_liked_by"
        or key == "edge_media_to_comment" %} {{value.count | int}}
    {%- elif key == "id" %} {{value | int}}
    {%- elif key == "accessibility_caption"
           or key == "display_url"
           or key == "shortcode"
           or key == "thumbnail_src"
           or key == "edge_media_to_caption"%} "{{value}}"
    {%- elif key == "location" -%}
        {%- if value == None -%}
            {"val": ""}
        {%- else -%}
            {"val": {{value}}}
        {%- endif -%}
    {%- else -%}{{value}}
    {%- endif -%}

    {%- if loop.last == false -%}
    ,
    {% endif %}
{% endfor %}
}$$)
AS (
{% for key, value in postData.items() -%}
{{key}}
    {%- if key == "accessibility_caption"
           or key == "shortcode"
           or key == "display_url"
           or key == "thumbnail_src"
           or key == "edge_media_to_caption" %} text
    {%- elif key == "edge_liked_by"
        or key == "edge_media_to_comment"
        or key == "taken_at_timestamp"%} int
    {%- elif key == "id" %} bigint
    {%- elif key == "thumbnail_resources" %} json array
    {%- elif key == "location" %} json
    {%- endif -%}

    {%- if loop.last == false -%}
    ,
    {% endif %}
{% endfor %}
);