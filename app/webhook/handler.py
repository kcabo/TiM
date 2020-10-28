import datetime
from app.models import db
from app.line_api import Event, notify
from app.gate import validate_user, UserNotFound
from app.webhook import dispatcher, humor


def handle(event_json):
    event = Event(event_json)

    if event.type == 'follow':
        notify(f'{event.line_id}から友達登録されました')
    elif event.type == 'unfollow':
        notify(f'{event.line_id}からブロックされました')
    elif event.type not in ['message', 'postback']:
        return 0

    # 操作中のメニューIDを取得
    try:
        event.menu_id = validate_user(event.line_id)
        if event.type == 'message':
            receive_message(event)
        else:
            receive_postback(event)

    # LINEIDによる検索にヒットしない=未登録
    except UserNotFound:
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
