from pymongo import MongoClient, collection
import random
from bs4 import BeautifulSoup
from PIL import Image, ImageFont, ImageDraw


def convert_to_picture(text):
    wraptext = [""]
    l = 0
    for i in text:
        fi = i
        delta = len(fi)
        if i == '\n':
            wraptext += [""]
            l = 0
        elif l + delta > 30:
            wraptext += [fi]
            l = delta
        else:
            wraptext[-1] += fi
            l += delta
    print(type(wraptext))
    i = Image.new("RGB", (500, len(wraptext) * 17 + 5), "#FFFFFF")
    d = ImageDraw.Draw(i)
    f = ImageFont.truetype("YaHeiYt.ttf", 16)
    for index in range(len(wraptext)):
        print(wraptext[index])
        d.text((2, 17 * index + 1), wraptext[index], font=f, fill='#000000')
    i.save('1.png')


def randomstory():
    client = MongoClient('127.0.0.1', 27017)
    db = client.jsxnh
    story_set = db.story
    storys = story_set.find()
    print(storys)
    ll = []
    for s in storys:
        print(s)
        ll.append(s)
    while True:
        story = random.choice(ll)
        my_set = collection.Collection(db, str(story.get('questionid')))
        answers = my_set.find({'islook': 0})
        ans = []
        for a in answers:
            ans.append(a)
        if len(ans) != 0:
            content = random.choice(ans)
            #my_set.update_one(content, {'$set': {'islook': 1}})
            content = content.get('content')
            content.replace('<br>', '\n')
            soup = BeautifulSoup(content, 'lxml')
            return story.get('question') + '?\n' + soup.get_text()


content = randomstory()
print(content)
print(len(content))
convert_to_picture(content)
'''
client = MongoClient('45.76.215.237', 27017)
db = client.jsxnh
story_set = db.story
storys = story_set.find()
for s in storys:
    print(s)
'''
