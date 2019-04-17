INSERT INTO ig_users(
{%- for key, value in userData.items() -%}
    {{key}}
    {%- if loop.last == false -%}
    ,
    {%- endif -%}
{%- endfor -%}
)
SELECT * FROM json_to_record($${
{% for key, value in userData.items() -%}
    "{{key}}":
    {%- if key == "edge_follow"
        or key == "edge_followed_by" %} {{value.count | int}}
    {%- elif key == "id" %} {{value | int}}
    {%- elif key == "biography"
        or key == "username"
        or key == "full_name"
        or key == "business_category_name"
        or key == "external_url"
        or key == "email"
        or key == "profile_pic_url" %} "{{value}}"
    {%- elif key == "is_business_account"
        or key == "is_verified" %} {{value | string | lower}}
    {%- elif key == "connected_fb_page" -%}
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
{% for key, value in userData.items() -%}
{{key}}
    {%- if key == "biography"
        or key == "username"
        or key == "full_name"
        or key == "business_category_name"
        or key == "external_url"
        or key == "email"
        or key == "profile_pic_url" %} text
    {%- elif key == "edge_follow"
        or key == "edge_followed_by"
        or key == "num_posts" %} int
    {%- elif key == "id" %} bigint
    {%- elif key == "search" %} int array
    {%- elif key == "is_business_account"
        or key == "is_verified" %} boolean
    {%- elif key == "connected_fb_page" %} json
    {%- endif -%}

    {%- if loop.last == false -%}
    ,
    {% endif %}
{% endfor %}
)
RETURNING id;