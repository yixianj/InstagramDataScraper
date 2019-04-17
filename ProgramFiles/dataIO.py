# dataIO.py
import codecs

def outputData(cur, tableName, fileName):
    targetFileName = "Tables/" + fileName + ".csv"
    cur.execute("SELECT * FROM tableName")
    with codecs.open(targetFileName, "w+", "utf-8") as targetFile:
        for row in cur:
            for col in row:
                targetFile.write(str(col) + ", ")
            targetFile.write('\n')
    cur.close()