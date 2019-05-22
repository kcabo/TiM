import os
import requests
import json


YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
headers =  {
    'Content-Type': 'application/json',
    'Authorization' : 'Bearer ' + YOUR_CHANNEL_ACCESS_TOKEN
}

def SendTextMsg(reply_token, text):
    url = 'https://api.line.me/v2/bot/message/reply'
    msgs = []
    for t in text: #引数2のメッセージをひとつずつリストに格納する
        msgs.append({
          'type' : 'text',
          'text' : t
        })
    data = {'replyToken': reply_token, 'messages': msgs}
    requests.post(url, headers=headers, data=json.dumps(data))
    return "ok"

def SendFlexMsg(reply_token):
    url = 'https://api.line.me/v2/bot/message/reply'
    msgs = [{
      "type": "flex",
      "altText": "This is a Flex Message",
      "contents": {
        "type": "bubble",
        "body": {
          "type": "box",
          "layout": "horizontal",
          "contents": [
            {
              "type": "text",
              "text": "Hello,"
            },
            {
              "type": "text",
              "text": "World!"
            }
          ]
        }
      }
    }]
    # for t in text: #引数2のメッセージをひとつずつリストに格納する
    #     msgs.append({
    #       'type' : 'text',
    #       'text' : t
    #     })
    data = {'replyToken': reply_token, 'messages': msgs}
    requests.post(url, headers=headers, data=json.dumps(data))
    return "ok"

def GetProfile(lineid):
    url = 'https://api.line.me/v2/bot/profile/{lineid}'.format(lineid=lineid)
    response = requests.get(url, headers=headers)
    js = response.json()
    return js['displayName']
