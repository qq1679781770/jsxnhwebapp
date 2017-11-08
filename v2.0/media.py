from basic import Basic
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


if __name__ == '__main__':
    print(get_media_ID('1.png'))
