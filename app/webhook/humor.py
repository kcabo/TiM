# 機能に直接は関係のないリプライ
# 会話したり、スタンプ送ったり
# ここから送られる際はアイコンが変わる

import os
import random
import requests


def smalltalk(event):
    reply = fetch_from_a3rt_api(event.text)
    msg_dic = {'type': 'text', 'text': reply}
    event.reply_with_icon(msg_dic)


def fetch_from_a3rt_api(query_text):
    A3RT_APIKEY = os.environ.get('A3RT_APIKEY') # これグローバル変数にするかも
    url = 'https://api.a3rt.recruit-tech.co.jp/talk/v1/smalltalk'
    data = {
        'apikey': A3RT_APIKEY,
        'query': query_text
    }
    raw_response = requests.post(url, data=data)
    response = raw_response.json()
    if response['status'] == 0: # 正常応答
        return response['results'][0]['reply']
    else:
        return response['message'] # 'apikey not found'などの理由が入る


def random_sticker(event):
    # Botから送れる3つのスタンプパッケージからスタンプを選ぶ
    package = random.randint(11537, 11539)
    if package == 11537:
        sticker = random.randint(52002734, 52002773)
    elif package == 11538:
        sticker = random.randint(51626494, 51626533)
    elif package == 11539:
        sticker = random.randint(52114110, 52114149)

    msg_dic = {
        "type": "sticker",
        "packageId": package,
        "stickerId": sticker
    }
    event.reply_with_icon(msg_dic)
