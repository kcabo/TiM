import datetime
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
        dispatcher.export_by_mail(event)

    # （開発用）LIFFのURLを返す
    elif text == 'テスト':
        import os
        LIFF_URL = os.environ['LIFF_URL']
        event.send_text(LIFF_URL)

    # タイムの取り込み
    elif text.find('\n') > 0:
        dispatcher.add_new_record(event)

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

        # メニュー選択
        elif obj == 'menu':
            menu_id = int(val)
            event.menu_id = menu_id
            dispatcher.view_records_scroll(event)
            event.aim_menu_id(menu_id)

        # タイム選択
        elif obj == 'rec':
            record_id = int(val)
            dispatcher.pick_record(event, record_id)

        # レコードの削除
        elif obj == 'delrec':
            record_id = int(val)
            dispatcher.delete_record(event, record_id)

        # メニュー削除の確認を問う
        elif obj == 'ask':
            menu_id = int(val)
            dispatcher.ask_whether_delete_menu(event, menu_id)

        # メニュー削除の確定
        elif obj == 'delmenu':
            menu_id = int(val)
            dispatcher.delete_menu(event, menu_id)

        # メニュー削除操作をキャンセル
        elif obj == 'cancel':
            event.send_text('やっぱりやめたよ')

        else:
            event.send_text(event.postback_data)
