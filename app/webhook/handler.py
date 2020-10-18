from app.models import db
from app import gate, line_api

class Event:
    def __init__(self, event_json):
        self.event_type = event_json.get('type')
        self.reply_token = event_json.get('replyToken')
        self.line_id = event_json.get('source', {'userId': None}).get('userId') # sourceキーがないときもある
        self.msg_type = event_json.get('message', {'type': None}).get('type')
        self.text = event_json.get('message', {'text': None}).get('text', None)
        self.postback_data = event_json.get('postback', {'data': None}).get('data')


def handle(event_json):
    e = Event(event_json)

    if e.event_type == 'follow':
        line_api.notify(f'{e.line_id}から友達登録されました')
    elif e.event_type == 'unfollow':
        line_api.notify(f'{e.line_id}からブロックされました')
    elif e.event_type not in ['message', 'postback']:
        return 0

    # イベントの発信者の持つ権限と操作中のメニューIDを取得
    state = gate.validate_user(e.line_id)
    if state.authorized:
        line_api.send_text(e.text)
    else:
        # TODO: まだ友達の人に権限を与えるためのフォームを送信する→LIFF
        pass
