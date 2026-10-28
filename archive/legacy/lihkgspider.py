import sqlite3
import requests
import json
import datetime
import cloudscraper


conn = sqlite3.connect(r'./lihkg.sqlite')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS lihkg_raw
    (id INTEGER PRIMARY KEY,
    title TEXT UNIQUE, no_of_reply INTEGER,
    no_of_uni_user_reply INTEGER,
    like_count INTEGER,
    dislike_count INTEGER,
    category TEXT,
    import_date TEXT)''')

headers = {"referer": "https://lihkg.com/category/1?order=hot"}
api = "https://lihkg.com/api_v2/thread/"
cat_id=2 #熱門
page=1
count=30

while True:
    complete_url = f"{api}hot?cat_id={cat_id}&page={page}&count=100&type=daily"
    res=cloudscraper.create_scraper().get(complete_url, headers=headers)
    #print("Status code is", res.status_code)
    count=count-1
    if res.status_code == 200:
        res=res.json()
        #info=json.loads(res.text)
        break
    if count==0:
        print('-------tried 30 times but all failed-------')
        input()
        break
    else:
        continue
#print(json.dumps(res,ensure_ascii=False, indent=2))


# save data in sqlite
today=datetime.date.today()

for n in res["response"]["items"]:
    title = n['title']
    no_of_reply = n['no_of_reply']
    no_of_uni_user_reply =n['no_of_uni_user_reply']
    like_count=n['like_count']
    dislike_count=n['dislike_count']
    category=n['category']['name']
    cur.execute('INSERT OR IGNORE INTO lihkg_raw (title, no_of_reply, no_of_uni_user_reply,like_count,dislike_count,category,import_date)VALUES (?,?,?,?,?,?,?)'
            , (title, no_of_reply, no_of_uni_user_reply,like_count,dislike_count,category,today) )

print('------done------')

conn.commit()
cur.close()
