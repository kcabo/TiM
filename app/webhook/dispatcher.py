import datetime

from app.models import db, Menu, Record, User
from app.webhook import flex, mailer
from app.webhook.csv_constructor import construct_csv


def view_menus(event, target_date: datetime.date):
    int_date = int(target_date.strftime('%y%m%d')) # unsafe
    menus = Menu.query.filter_by(date=int_date).order_by(Menu.menuid).all()
    flex_menus = flex.build_menus(target_date, menus)
    alt_text = 'メニュー一覧'
    event.send_flex(alt_text, [flex_menus])

    # メニューが登録されていればそのメニューを選択していることにする
    # そうでないと一覧→メールと送った際にどの日付を指定しているか不明になる
    if menus:
        first_menu_id = menus[0].menuid
        event.aim_menu_id(first_menu_id)
    else:
        event.aim_menu_id(0)


def view_records_scroll(event):
    menu_q = fetch_current_menu(event)
    if menu_q is None: return None

    # タイムを全取得
    records = Record.query.filter_by(menuid=event.menu_id).all()

    flex_menu_transaction = flex.build_menu_transaction(menu_q)
    flex_records_scroll = flex.build_records_scroll(records)
    flex_msgs = [flex_menu_transaction, flex_records_scroll]

    alt_text = 'タイム一覧'
    event.send_flex(alt_text, flex_msgs)


def export_by_mail(event):
    menu_q = fetch_current_menu(event)
    if menu_q is None: return None

    int_date = menu_q.date
    all_menus = Menu.query.filter_by(date=int_date).order_by(Menu.menuid).all()
    csv = construct_csv(all_menus)

    target_date = datetime.datetime.strptime(str(int_date),'%y%m%d').date()
    user = User.query.filter_by(lineid=event.line_id).one()

    try:
        mailer.send_mail_with_csv(user, csv, target_date)

    # メールがうまく送れなかったときにFeedback
    except Exception as e:
        event.send_text('メール送信に失敗しました...')
    else:
        event.send_thank_msg()


def fetch_current_menu(event):
    menu_id = event.menu_id
    if menu_id == 0:
        event.send_text('メニューを選択してください！')
        return None

    menu_q = Menu.query.get(menu_id)
    if menu_q is None:
        event.send_text('メニューが見つかりませんでした...')
        return None
    else:
        return menu_q

# with open('de.py', 'w', encoding='UTF8') as f:
#     import json
#     print(json.dumps(flex_menu_transaction), file=f)
