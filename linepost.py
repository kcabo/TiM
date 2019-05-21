import os
import requests
import json


YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
# YOUR_CHANNEL_ACCESS_TOKEN = "j"
url = 'https://api.line.me/v2/bot/message/reply'
headers =  {
    'Content-Type': 'application/json',
    'Authorization' : 'Bearer ' + YOUR_CHANNEL_ACCESS_TOKEN
}

def SendReplyMsg(reply_token, text):
    msgs = []
    for t in text: #引数2のメッセージをひとつずつリストに格納する
        msgs.append({
          'type' : 'text',
          'text' : t
        })

    data = {'replyToken': reply_token, 'messages': msgs}

    requests.post(url, headers=headers, data=json.dumps(data))

    return "ok"
