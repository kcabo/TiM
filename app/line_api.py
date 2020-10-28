import os
import requests

from app.redis_setup import conn

ACCESS_TOKEN = os.environ['CHANNEL_ACCESS_TOKEN']
ENVIRONMENT = os.environ['ENVIRONMENT'] # 環境判定

class Event:
    def __init__(self, event_json):
        self.type = event_json.get('type')
        self.reply_token = event_json.get('replyToken')
        self.line_id = event_json.get('source', {'userId': None}).get('userId') # sourceキーがないときもある
        self.text = event_json.get('message', {'text': None}).get('text')
        self.postback_data = event_json.get('postback', {'data': None}).get('data')
        self.picker_date = event_json.get('postback', {'params': {}}).get('params', {'date': None}).get('date')
        self.menu_id = 0


    def reply(self, msg_list):
        if not msg_list: return 0
        headers =  {
            'Content-Type': 'application/json',
            'Authorization' : 'Bearer ' + ACCESS_TOKEN
        }
        url = 'https://api.line.me/v2/bot/message/reply'
        data = {'replyToken': self.reply_token, 'messages': msg_list}

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


    def send_text(self, *texts):
        msg_list = [{'type': 'text', 'text': t} for t in texts if t is not None]
        self.reply(msg_list)


    def send_flex(self, alt_text, flex_msgs: list):
        msg_list = [{
            'type': 'flex',
            'altText': alt_text,
            'contents': flex
        } for flex in flex_msgs if flex is not None]
        self.reply(msg_list)


    def reply_with_icon(self, msg_dic):
        url = 'https://static.thenounproject.com/png/335121-200.png'
        msg_dic['sender'] = {
            'iconUrl': url
        }
        self.reply([msg_dic])


    def aim_menu_id(self, new_menu_id: int):
        conn.set(self.line_id, new_menu_id)


def notify(message):
    LINE_NOTIFY_ACCESS_TOKEN = os.environ['NOTIFY_ACCESS_TOKEN']
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': 'Bearer ' + LINE_NOTIFY_ACCESS_TOKEN}
    data = {'message': message}
    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        print(response.json())
        raise Exception('LINE Notifyによる通知に失敗')
