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

    # スタンプや画像などテキスト以外のメッセージを受信したらスタンプを返す
    if text is None:
        humor.random_sticker(event)

    # メニュー一覧
    elif text == '一覧':
        today = datetime.date.today()
        dispatcher.view_menus(event, today)

    # 操作中のメニューのタイムの確認
    elif text == '確認':
        dispatcher.view_records_scroll(event)

    # メールで出力
    elif text == 'メール':
        humor.random_sticker(event)

    # タイムの取り込み
    elif text.find('\n') > 0:
        # TODO: 文字列エスケープ
        humor.random_sticker(event)

    # 雑談
    else:
        humor.smalltalk(event)


def receive_postback(event):
    try:
        obj, val = event.postback_data.split('=')

    except ValueError:
        event.send_text('アンパックできませんでした')

    else:
        # メニュー一覧（三角ボタン押して日付変更した場合）
        if obj == 'date':
            target_date = datetime.datetime.strptime(val, '%y%m%d')
            dispatcher.view_menus(event, target_date)

        # メニュー一覧（DatePicker使用した場合）
        elif obj == 'picker':
            val = event.picker_date
            target_date = datetime.datetime.strptime(val, '%Y-%m-%d')
            dispatcher.view_menus(event, target_date)
        else:
            event.send_text(event.postback_data)
