#!/usr/bin/env python3
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
insertRawUserDataP1 = """INSERT INTO raw_user_data(user_data) VALUES (' """
insertRawUserDataP2 = """');"""
updateUserTemp = env.get_template('updateUserTable.sql')
insertSearchForUser = env.get_template('insertSearchForUser.sql')

def updateUserAndPostData(cur, conn, scraperInput, userData, searchId):
    print("UPDATING USER DATA")
    cur.execute("SELECT search FROM ig_users WHERE id = " + userData["id"] + ";")
    search = cur.fetchone()[0]
    if searchId in search:
        return
    userData["search"] = search.append(searchId)
    if (scraperInput["search"]["email"] != ""):
        userData["email"] = clean.extractEmails(userData["biography"], scraperInput["search"]["email"])
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

    users = search.searchGoogleCSE(scraperInput, cur, conn)

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
            except LookupError as lookupErr:
                print("LookupError: key or index does not exist.")
                print(lookupErr)
                print("### postData ###\n" + str(postData))
                pass

            insertPostQuery = insertPostTemp.render(postData = postData)

            try:
                cur.execute(insertPostQuery)
            except psycopg2.IntegrityError as duplicateErr:
                print("errorPsycopg2: duplicateErr. Post already stored.")
                print(duplicateErr)
                conn.rollback()
                pass
            except psycopg2.InternalError as internalErr:
                print("errorPsycopg2: internalErr")
                print(internalErr)
            else:
                conn.commit()
                print("INSERT ROW IN POSTS")
        print("Finished posts for a user")
    print("Finished inserting data into tables: ig_users, post_data")

    # Output data
    dataIO.outputData(cur, "ig_users", scraperInput["io"]["filename"])

def main():
    instagramDataScraper()

if __name__=="__main__":
    main()