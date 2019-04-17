# search.py
from googleapiclient.discovery import build
from urllib.request import urlopen
from bs4 import BeautifulSoup
from http import client
import urllib.error
import json
import psycopg2
import psycopg2.extensions
import extractData
import socket

insertRawUserDataP1 = """INSERT INTO raw_user_data(user_data) VALUES ($$ """
insertRawUserDataP2 = """$$);"""

def searchGoogleCSE(scraperInput, cur, conn):
    users = []
    service = build("customsearch", "v1",
                    developerKey="AIzaSyBhazBCynmi_LJsc8ZrgUs5bBLcSmpC024")
    page = 1
    userNum = 0
    while (page < 100):
        res = service.cse().list(
            q=scraperInput["googleCSE"]["query"], # search query
            exactTerms=scraperInput["googleCSE"]["exact_terms"],
            cr=scraperInput["googleCSE"]["country"], # Country / Location requirement
            cx='008348639631699998524:tonjuejsga4', # Custom search engine id
            start=page, # Starting result number
            num=10 # Number of results per page -- Max 10
        ).execute()
        # Increment to next page
        page += 10

        # Loop through each result item on the current page
        # Open result's instagram link, scrape instagram data from link page
        for item in res['items']:
            try:
                webpage = urlopen(item['link'])
                instaSoup = BeautifulSoup(webpage, 'html.parser')
                webpage.close()
                script = instaSoup.find('script', text=lambda t: t.startswith('window._sharedData'))
                pageJson = script.text.split(' = ', 1)[1].rstrip(';')
                data = json.loads(pageJson)
            except urllib.error.HTTPError as httpErr:
                print("urllibError: httpErr")
                print(httpErr)
                continue
            except ConnectionResetError as connResetErr:
                print("connectionResetError: connResetErr - Connection was reset, skip.")
                print(connResetErr)
                continue
            except client.IncompleteRead as incomplReadErr:
                print("httpErr: Incomplete read")
                print(incomplReadErr)
                continue
            except urllib.error as urllibErr:
                print("urllibError: generalErr")
                print(urllibErr)
                continue
            except socket.timeout as timeoutErr:
                print("socketErroro: timeoutErr")
                print(timeoutErr)
            except Exception as e:
                print("Unexpected error")
                print(e)
                continue

            try:
                users.append(data['entry_data']['ProfilePage'][0]['graphql']['user'])
            except:
                print("assignUserDataError: JSON User data cannot be extracted")
                continue

            try:
                userData = extractData.getUserData(data['entry_data']['ProfilePage'][0]['graphql']['user'])
                cur.execute(insertRawUserDataP1 + json.dumps(userData) + insertRawUserDataP2)
                conn.commit()
                print("INSERT ROW INTO: raw_user_data")
            except psycopg2.ProgrammingError as progErr:
                print("psycopg2Err: progErr")
                print(progErr)
                print("Can't insert data")
                print("###USERDATA###\n" + json.dumps(userData))
                print("\n###QUERY###\n" + insertRawUserDataP1 + json.dumps(userData) + insertRawUserDataP2)
                exit(1)
    print("Finished GoogleCSE search\n# Results: " + str(len(users)))
    return users