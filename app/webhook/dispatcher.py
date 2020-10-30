import datetime

from app.models import db, Menu, Record
from app.webhook import flex


def view_menus(event, target_date: datetime.date):
    int_date = int(target_date.strftime('%y%m%d')) # unsafe
    menus = Menu.query.filter_by(date=int_date).order_by(Menu.menuid).all()
    flex_menus = flex.build_menus(target_date, menus)
    alt_text = 'メニュー一覧'
    event.send_flex(alt_text, [flex_menus])
    event.aim_menu_id(0)


def view_records_scroll(event):
    menu_id = event.menu_id
    if menu_id == 0:
        event.send_text('メニューを選択してください！')
        return None

    # タイムを見たいメニューを取得
    menu = Menu.query.get(menu_id)
    if menu is None:
        event.send_text('メニューが見つかりませんでした...')
        return None

    # タイムを全取得
    records = Record.query.filter_by(menuid=menu_id).all()

    flex_menu_transaction = flex.build_menu_transaction(menu)
    flex_records_scroll = flex.build_records_scroll(records)
    flex_msgs = [flex_menu_transaction, flex_records_scroll]

    alt_text = 'タイム一覧'
    event.send_flex(alt_text, flex_msgs)

# with open('de.py', 'w', encoding='UTF8') as f:
#     import json
#     print(json.dumps(flex_menu_transaction), file=f)
