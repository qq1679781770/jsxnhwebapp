from run import app
from flask import  request, make_response
import hashlib
import random
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import time
from PIL import Image, ImageFont, ImageDraw
from basic import Basic
from models import Account,Story
import requests


def get_media_ID(path):
    img_url = 'https://api.weixin.qq.com/cgi-bin/media/upload'
    payload_img = {
        'access_token': Basic().get_access_token(),
        'type': 'image'
    }
    data = {'media': open(path, 'rb')}
    r = requests.post(url=img_url, params=payload_img, files=data)
    dict = r.json()
    return dict['media_id']


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
    i = Image.new("RGB", (500, len(wraptext) * 17 + 5), "#FFFFFF")
    d = ImageDraw.Draw(i)
    f = ImageFont.truetype("YaHeiYt.ttf", 16)
    for index in range(len(wraptext)):
        d.text((2, 17 * index + 1), wraptext[index], font=f, fill='#000000')
    i.save('1.png')


def randomstory():
    while True:
        num = Story.count()
        id = random.choice([i for i in range(1,num+1)])
        story = Story.find(id)
        if story.islook is 1:
            continue
        content = story.content
        content.replace('<br>', '\n')
        soup = BeautifulSoup(content, 'lxml')
        story.islook = 1;
        story.update()
        return story.get('question')+'?\n'+soup.get_text()


@app.route('/wx', methods=['GET', 'POST'])
def weixin():
    if request.method == 'GET':
        try:
            data = request.args
            signature = data.get('signature')
            print(signature)
            timestamp = data.get('timestamp')
            print(timestamp)
            nonce = data.get('nonce')
            print(nonce)
            echostr = data.get('echostr')
            print(echostr)
            token = 'jsxnh'
            list = [token, timestamp, nonce]
            list.sort()
            sha1 = hashlib.sha1()
            map(sha1.update, list)
            hashcode = sha1.hexdigest()
            if True:
                return echostr
            else:
                return ""
        except Exception as e:
            return e
    else:
        rec = request.stream.read()
        xml_recv = ET.fromstring(rec)
        ToUserName = xml_recv.find("ToUserName").text
        FromUserName = xml_recv.find("FromUserName").text
        Content = xml_recv.find("Content").text
        re = "<xml><ToUserName><![CDATA[%s]]></ToUserName>"\
             "<FromUserName><![CDATA[%s]]></FromUserName>"\
             "<CreateTime>%s</CreateTime>"\
             "<MsgType><![CDATA[text]]></MsgType>"\
             "<Content><![CDATA[%s]]></Content></xml>"
        if Content == u'故事':
            reply = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]>" \
                    "</FromUserName><CreateTime>%s" \
                    "</CreateTime><MsgType><![CDATA[image]]></MsgType><Image>"\
                    "<MediaId><![CDATA[%s]]></MediaId>"\
                    "</Image></xml>"
            recv_content = randomstory()
            convert_to_picture(recv_content)
            msgid = get_media_ID('1.png')
            response = make_response(reply % (FromUserName, ToUserName, str(int(time.time())), msgid))
            response.content_type = 'application/xml'
            return response
        elif Content == u'allcount':
            accounts = Account.findAll()
            recv_content = ''
            for account in accounts:
                recv_content += account.getValue('id')+' '
                recv_content += account.getValue('app')+' '
                recv_content += account.getValue('account')+' '
                recv_content += account.getValue('password')+' '
                recv_content += account.getValue('message')+' '
            response = make_response(re % (FromUserName, ToUserName, str(int(time.time())), recv_content))
            response.content_type = 'application/xml'
            return response
        elif len(Content.split(' ')) >= 2:
            keyworks = Content.split(' ')
            keywork = keyworks[0]
            response = make_response(re % (FromUserName, ToUserName, str(int(time.time())), "ok"))
            response.content_type = 'application/xml'
            if keywork == u'add':
                acc = Account(id=keyworks[1], app=keyworks[2], account=keyworks[3], password=keyworks[4], message=keyworks[5])
                acc.save()
                return response
            elif keywork == u'remove':
                acc = Account.find(keyworks[1])
                acc.remove()
                return response
            elif keywork == u'update':
                acc = Account.find(keyworks[1])
                acc.app=keyworks[2]
                acc.account = keyworks[3]
                acc.password = keyworks[4]
                acc.message = keyworks[5]
                acc.update()
                return response
            elif keywork == u'find':
                acc = Account.find(keyworks[1])
                accstr = acc.account+"\n"+acc.password
                response_ = make_response(re % (FromUserName, ToUserName, str(int(time.time())), accstr))
                response_.content_type = 'application/xml'
                return response_
            else:
                return "success"
        else:
            return 'success'


