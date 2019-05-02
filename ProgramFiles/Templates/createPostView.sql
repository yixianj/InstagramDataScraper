DROP VIEW IF EXISTS post_data_view;
CREATE VIEW post_data_view AS(
    SELECT p.owner, u.username, u.email,
        AVG(p.edge_liked_by) AS avg_likes,
        AVG(p.edge_media_to_comment) AS avg_comments
    FROM post_data p, ig_users u
    WHERE p.owner = u.id
    GROUP BY owner, u.username, u.email
    ORDER BY AVG(p.edge_liked_by) DESC, AVG(p.edge_media_to_comment) DESC
    );