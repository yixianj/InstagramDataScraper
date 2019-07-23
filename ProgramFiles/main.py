#!/usr/bin/env python3
# Instagram scraper using GoogleCSE
# programmed by: Adina (Yixian) Jia 2019
# https://github.com/yixianj
from jinja2 import Template, FileSystemLoader, Environment
import json
import extractData
import cleanData as clean
import dataIO
import psycopg2
import search
import datetime

##### Global variables #####
# Dictionary of input data, read from file
# scraperInput = {}
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)
env.trim_blocks = True
env.lstrip_blocks = True
env.rstrip_blocks = True
insertUserTemp = env.get_template('insertUserData.sql')
insertPostTemp = env.get_template('insertPostData.sql')
insertSearchDataTemp = env.get_template('insertSearchData.sql')
getRecordIdTemp = env.get_template('getRecordId.sql')
updateUserTemp = env.get_template('updateUserTable.sql')
insertSearchForUser = env.get_template('insertSearchForUser.sql')
createPostViewTemp = env.get_template('createPostView.sql')

"""
Updates an existing row in the ig_users table
using data from the json object in the paramater userData.
After updating the user row,
new posts by this user are added to the post_data table.

scraperInput is the json object read from scraperInput.json
searchId is the integer id of the search being conducted; stored in search_data
"""
def updateUserAndPostData(cur, conn, scraperInput, userData, searchId):
    print("UPDATING USER DATA")
    cur.execute("SELECT search FROM ig_users WHERE id = " + userData["id"] + ";")
    search = cur.fetchone()[0]
    if searchId in search:
        return
    userData["search"] = search.append(searchId)
    if (scraperInput["search"]["email"] != ""):
        userData["email"] = clean.extractEmails(userData["biography"], scraperInput["search"]["email"])
    if "edge_owner_to_timeline_media" in userData:
        userData["num_posts"] = userData["edge_owner_to_timeline_media"]["count"]
    userData["full_name"] = clean.removeEmojisAndOther(userData["full_name"])
    userData["biography"] = clean.removeEmojisAndOther(userData["biography"])
    updateUserQuery = updateUserTemp.render(tableName = "ig_users", userData = userData,
                                            id = userData["id"],
                                            searchId = searchId)
    try:
        cur.execute(updateUserQuery)
    except psycopg2.error as psycopErr:
        print("UPDATE USER QUERY:\n" + updateUserQuery)
        print("errorPsycopg2: pscyopErr")
        print(psycopErr)
        exit(1)
    else:
        conn.commit()
        print("UPDATED ROW IN USERS")
"""
Main function of this Instagram Data scraper
Connects to a psql database
Inserts row in search_data,
Conducts googleCSE search using inputs read from scraperInput.json

For each page of results, for each result in the page
Opens link, and if it is a profile page it will:
    Inserts rows in ig_users table, then rows in post_data for this ig_user
    
Error messages are printed when desired data cannot be extracted (i.e. not a profile page)
or link cannot be open

Outputs data into file specified in scraperInput.json
"""
def instagramDataScraper():
    print("Reading input from scraperInput.json")
    with open("scraperInput.json", "r+") as inputFile:
        scraperInput = json.load(inputFile)

        # Connect to database
        connectToDB = ("host=" + scraperInput["psql"]["host"] + " " +
                       "dbname=" + scraperInput["psql"]["dbname"] + " " +
                       "user=" + scraperInput["psql"]["user"] + " " +
                       "password=" + scraperInput["psql"]["password"])

        try:
            conn = psycopg2.connect(connectToDB)
        except:
            print("Error: Error connecting to Database")
            exit(1)
        conn.set_client_encoding('utf-8')
        cur = conn.cursor()

    print("##### Beginning Search #####")
    # Insert row in search_data
    currDate = datetime.datetime.now()
    scraperInput["date"] = str(currDate)
    insertSearchDataQuery = insertSearchDataTemp.render(googleCSE = json.dumps(scraperInput["googleCSE"]),
                                                        search = json.dumps(scraperInput["search"]),
                                                        date = scraperInput["date"],
                                                        io = json.dumps(scraperInput["io"]))
    cur.execute(insertSearchDataQuery)
    print("Insert row in: search_data")

    # Get id of search_data row to refer to for user rows
    # This way we know which searches each user shows up in
    #getRecordIdQuery = getRecordIdTemp.render()
    #cur.execute(getRecordIdQuery)
    searchId = cur.fetchone()[0]

    # Specify if rows should be inserted into raw users table
    # True to insert, False otherwise
    users = search.searchGoogleCSE(scraperInput, cur, conn, False)

    for user in users:
        userData = extractData.getUserData(user)
        try:
            userData["search"] = [searchId]
            if (scraperInput["search"]["email"] != ""):
                userData["email"] = clean.extractEmails(userData["biography"], scraperInput["search"]["email"])
            userData["num_posts"] = user["edge_owner_to_timeline_media"]["count"]
            userData["full_name"] = clean.removeEmojisAndOther(userData["full_name"])
            userData["biography"] = clean.removeEmojisAndOther(userData["biography"])
        except LookupError as lookupErr:
            print("LookupError: could not find key or index.")
            print(lookupErr)
            print("### userData ###\n" + str(userData))
            pass

        insertUserQuery = insertUserTemp.render(userData=userData)
        try:
            cur.execute(insertUserQuery)
            insertSearchForUserQuery = insertSearchForUser.render(id = cur.fetchone()[0], searchId = searchId)
            cur.execute(insertSearchForUserQuery)
        except psycopg2.DataError as dataErr:
            print("errorPsycopg2: dataErr")
            print(dataErr)
            print("insertUserQuery:\n" + insertUserQuery)
            exit(1)
        except psycopg2.IntegrityError as duplicateErr:
            print("errorPsycopg2: duplicateErr")
            print(duplicateErr)
            conn.rollback()
            updateUserAndPostData(cur, conn, scraperInput, userData, searchId)
            pass
        except psycopg2.InternalError as internalErr:
            print("errorPsycopg2: internalErr")
            print(internalErr)
        except psycopg2.ProgrammingError as programErr:
            print("errorPscyopg2: programErr")
            print(programErr)
            print("QUERY:\n" + insertUserQuery)
        else:
            conn.commit()
            print("INSERT ROW IN USERS")

        edges = user["edge_owner_to_timeline_media"]["edges"]
        for item in edges:
            try:
                postData = extractData.getPostData(item["node"])
                postData["location"] = json.dumps(postData["location"])
                postData["thumbnail_resources"] = json.dumps(postData["thumbnail_resources"])
                postData["edge_media_to_caption"] = clean.removeEmojisAndOther(postData["edge_media_to_caption"]
                                                                    ["edges"][0]["node"]
                                                                    ["text"])
                postData["owner"] = userData["id"]
            except LookupError as lookupErr:
                print("LookupError: key or index does not exist.")
                print(lookupErr)
                #print("### postData ###\n" + str(postData))
                pass

            insertPostQuery = insertPostTemp.render(postData = postData)

            try:
                cur.execute(insertPostQuery)
            except psycopg2.IntegrityError as duplicateErr:
                print("errorPsycopg2: duplicateErr. Post already stored.")
                print(duplicateErr)
                conn.rollback()
                break
            except psycopg2.InternalError as internalErr:
                print("errorPsycopg2: internalErr")
                print(internalErr)
            except psycopg2.errors.SyntaxError as syntaxError:
                print("errorPsycopg2: syntaxErr")
                print(syntaxErr)
                print("Query\n", insertPostQuery)
                exit(1)
            else:
                conn.commit()
                print("INSERT ROW IN POSTS")
        print("Finished posts for a user")
    print("Finished inserting data into tables: ig_users, post_data")

    # Create Post View Query from stored data in ig_users and post_data
    # Users listed in descending order of most likes, then comments
    # In other words, most popular users are listed first
    cur.execute(createPostViewTemp.render())
    print("Finished create post_data_view")

    # Output data
    dataIO.outputData(cur, "ig_users", scraperInput["io"]["filename"])
    print("Finished outputting file")
    cur.close()

    print("##### Instagram Data Scraper has finished execution #####")

def main():
    instagramDataScraper()

if __name__=="__main__":
    main()