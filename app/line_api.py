import os
import requests

ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'DEVELOP') # 環境判定


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

    # 以下テスト用
    if ENVIRONMENT == 'DEVELOP':
        MY_LINE_ID = os.environ.get('MY_LINE_ID')
        url = 'https://api.line.me/v2/bot/message/push'
        data = {'to': MY_LINE_ID, 'messages': msg_list}
    # テスト用ここまで

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print(response.json())
        raise Exception('Botからのメッセージ送信に失敗')


def notify(message):
    LINE_NOTIFY_ACCESS_TOKEN = os.environ.get('NOTIFY_ACCESS_TOKEN')
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': 'Bearer ' + LINE_NOTIFY_ACCESS_TOKEN}
    data = {'message': message}
    response = requests.post(url, headers=headers, params=data)
    if response.status_code != 200:
        print(response.json())
        raise Exception('LINE Notifyによる通知に失敗')
