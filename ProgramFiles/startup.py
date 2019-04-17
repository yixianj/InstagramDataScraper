#!/usr/bin/env python3

import psycopg2
import json

def runSQLFile(cur, conn, filename):
    cur.execute(open(filename, "r").read())
    conn.commit()
    print("Successfully ran: " + filename)

def main():
    print("##### Beginning Startup of Instagram Data Scraper #####")

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

    runSQLFile(cur, conn, "Templates/dropTables.sql")
    runSQLFile(cur, conn, "Templates/createTables.sql")

    conn.commit()

    print("##### Startup was successful #####")

if __name__== "__main__":
    main()