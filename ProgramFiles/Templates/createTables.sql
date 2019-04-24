/* Create tables */
CREATE TABLE raw_user_data(
    id BIGSERIAL,
    user_data json,
    PRIMARY KEY (id)
);

CREATE TABLE search_data(
	id BIGSERIAL,
    search_date timestamptz,
    googleCSE json,
    search json,
    io json,
    PRIMARY KEY (id)
);

CREATE TABLE ig_users(
    biography text,
    business_category_name text,
    connected_fb_page json,
    edge_follow int,
    edge_followed_by int,
    email text,
    external_url text,
    full_name text,
    id bigint,
    is_business_account boolean,
    is_verified boolean,
    num_posts int,
    profile_pic_url text,
    search int array,
    username text,
    PRIMARY KEY (id)
);

CREATE TABLE post_data(
    accessibility_caption text,
    display_url text,
    edge_liked_by int,
    edge_media_to_caption text,
    edge_media_to_comment int,
    id bigint,
    location json,
    shortcode text,
    taken_at_timestamp int,
    thumbnail_resources json array,
    thumbnail_src text,
    PRIMARY KEY (id)
);