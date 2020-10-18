import os
import requests

ACCESS_TOKEN = os.environ['CHANNEL_ACCESS_TOKEN']


def send_text(reply_token, *texts):
    msg_list = [{'type': 'text', 'text': t} for t in texts if t is not None]
    reply(reply_token, msg_list)

def reply(reply_token, msg_list):
    if not msg_list: return 0
    headers =  {
        'Content-Type': 'application/json',
        'Authorization' : 'Bearer ' + ACCESS_TOKEN
    }
    url = 'https://api.line.me/v2/bot/message/reply'
    data = {'replyToken': reply_token, 'messages': msg_list}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print(response.json())
        raise Exception('Reply ERROR')

def notify(message):
    LINE_NOTIFY_ACCESS_TOKEN = os.environ['NOTIFY_ACCESS_TOKEN']
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': 'Bearer ' + LINE_TOKEN}
    data = {'message': message}
    response = requests.post(url, headers=headers, params=data)
    if response.status_code != 200:
        print(response.json())
        raise Exception('Notify ERROR')
