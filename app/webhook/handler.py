import datetime
from app.models import db
from app import gate, line_api
from app.webhook import dispatcher, humor


class Event:
    def __init__(self, event_json):
        self.type = event_json.get('type')
        self.reply_token = event_json.get('replyToken')
        self.line_id = event_json.get('source', {'userId': None}).get('userId') # sourceキーがないときもある
        self.text = event_json.get('message', {'text': None}).get('text')
        self.postback_data = event_json.get('postback', {'data': None}).get('data')
        self.menu_id = 0
        print(event_json.get('postback', None), 'ポストバックデータ見せる')

    def reply(self, msg_list):
        line_api.post_reply(self.reply_token, msg_list)


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


def handle(event_json):
    event = Event(event_json)

    if event.type == 'follow':
        line_api.notify(f'{event.line_id}から友達登録されました')
    elif event.type == 'unfollow':
        line_api.notify(f'{event.line_id}からブロックされました')
    elif event.type not in ['message', 'postback']:
        return 0

    # 操作中のメニューIDを取得
    try:
        event.menu_id = gate.validate_user(event.line_id)
        if event.type == 'message':
            receive_message(event)
        else:
            receive_postback(event)

    # LINEIDによる検索にヒットしない=未登録
    except gate.UserNotFound:
        # TODO: まだ友達の人に権限を与えるためのフォームを送信する→LIFF
        msg = 'まだユーザー登録されておりません。管理者に登録をお願いしてください。'
        event.send_text(msg)


def receive_message(event):
    text = event.text
    if text is None:
        humor.random_sticker(event)
    elif text == '一覧':
        today = datetime.date.today()
        dispatcher.view_menus(event, today)
    elif text == '確認':
        humor.random_sticker(event)
    elif text == 'メール':
        humor.random_sticker(event)
    elif text.find('\n') > 0:
        # TODO: 文字列エスケープ
        humor.random_sticker(event)
    else:
        humor.smalltalk(event)


def receive_postback(event):
    print(event.postback_data)
    event.send_text(event.postback_data)
