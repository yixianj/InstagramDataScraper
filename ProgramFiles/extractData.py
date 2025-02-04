# extractData.py

searchDataTableFields = [
    "google_CSE",
    "search",
    "search_date",
    "io"
]

keptUserData = [
    "edge_follow",
    "edge_followed_by",
    "external_url",
    "full_name",
    "id",
    "is_business_account",
    "is_verified",
    "username",
    "biography",
    "business_category_name",
    "connected_fb_page",
    "profile_pic_url"
]
keptNodeData = [
    "accessibility_caption",
    "display_url",
    "edge_liked_by",
    "edge_media_to_caption",
    "edge_media_to_comment",
    "id",
    "location",
    "owner",
    "shortcode",
    "taken_at_timestamp",
    "thumbnail_resources",
    "thumbnail_src"
]

"""
Extracts key,value pairs from userData json object
that has a key in keptUserData
Returns kept pairs in a dictionary
"""
def getUserData(userData):
    user = {k: userData[k] for k in keptUserData if k in userData}
    return user

"""
Extracts key, value pairs from nodeData json object
that has a key in keptNodeData
Returns kept pairs in a dictionary
"""
def getPostData(nodeData):
    post = {k: nodeData[k] for k in keptNodeData if k in nodeData}
    return post