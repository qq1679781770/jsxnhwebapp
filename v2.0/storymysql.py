from pymongo import MongoClient, collection
import random
import pymysql,pymysql.cursors



config = {
    'host': '45.76.215.237',
    'port': 3306,
    'user': 'jsxnh',
    'password': 'jsxnh',
    'db':'jsxnh',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}
conn = pymysql.connect(**config)
try:
    with conn.cursor() as cur:
        cur.execute("select count(*) num from story")
        rs = cur.fetchall()
        print(rs[0]['num'])
    conn.commit()
    conn.close()
except:
    conn.close()
client = MongoClient('127.0.0.1', 27017)
db = client.jsxnh
story_set = db.story
storys = story_set.find()
print(storys)
counts = 0;
for s in storys:
    my_set = collection.Collection(db, str(s.get('questionid')))
    question = s.get('question')
    answers = my_set.find()
    for a in answers:
        '''
        sql = "insert into story(question,content,islook) values('"+question+"','"+a.get('content')+"',0)"
        print(sql)
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                conn.commit()
        except:
            conn.rollback()
        '''
        counts = counts+1;
print(counts)

arr = [y for y in range(1,10000)]
print(arr)

