import sqlite3
db = "tweet-data.db"

conn = sqlite3.connect(db)
c = conn.cursor()

#use this try block when new table added in db
#added all previous table name to add new table
try:
    c.execute("drop table lang_data")
    c.execute("drop table trend_data")
    c.execute("drop table twt_data")
    c.execute("drop table country_data")
    c.execute("drop table love_data")
    c.execute("drop table pro_lang_data")
except:
    pass

cmd = "CREATE TABLE lang_data (language TEXT, top_lang TEXT, datetime TEXT)"
c.execute(cmd)

cmd = "CREATE TABLE trend_data (trend TEXT, trend_id1 TEXT, trend_id2 TEXT, trend_id3 TEXT, datetime TEXT)"
c.execute(cmd)

cmd = "CREATE TABLE twt_data (top_tweet TEXT, datetime TEXT)"
c.execute(cmd)

cmd = "CREATE TABLE country_data (country TEXT, datetime TEXT)"
c.execute(cmd)

cmd = "CREATE TABLE love_data (love_words INT, swear_words INT, datetime TEXT)"
c.execute(cmd)

cmd = "CREATE TABLE pro_lang_data (pro_lang TEXT, datetime TEXT)"
c.execute(cmd)


conn.commit()
conn.close()
