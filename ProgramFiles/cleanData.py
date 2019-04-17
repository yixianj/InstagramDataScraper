# cleanData.py
import re

def averageLikes(posts, numPosts):
    avgLikes = 0
    postNum = 0
    while (postNum < numPosts):
        avgLikes += posts[postNum]['node']['edge_liked_by']['count']
        postNum += 1
    return (avgLikes / numPosts)

def removeEmojisAndOther(word):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]+", flags=re.UNICODE)
    no_emoji = emoji_pattern.sub(r'', word) # no emoji
    return str(no_emoji.encode("utf-8")).replace('"', "'").replace("\\", " ").replace("/", " ")

def extractEmails(userBio, email):
    bio = userBio.split()
    for word in bio:
        if (email in word):
            return removeEmojisAndOther(word)