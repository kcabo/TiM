import datetime
from itertools import zip_longest

from app.models import db, Menu, Record, User
from app.webhook import flex, mailer


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
    if menu_q is None:
        return None

    # タイムを全取得
    records = Record.query.filter_by(menuid=event.menu_id).all()

    flex_menu_transaction = flex.build_menu_transaction(menu_q)
    flex_records_scroll = flex.build_records_scroll(records)
    flex_msgs = [flex_menu_transaction, flex_records_scroll]

    alt_text = 'タイム一覧'
    event.send_flex(alt_text, flex_msgs)


def export_by_mail(event):
    menu_q = fetch_current_menu(event)
    if menu_q is None:
        return None
    int_date = menu_q.date
    all_menus = Menu.query.filter_by(date=int_date).order_by(Menu.menuid).all()

    csv_strings = [construct_csv(menu) for menu in all_menus]
    csv = '\r\n.\r\n'.join(csv_strings)

    target_date = datetime.datetime.strptime(str(int_date),'%y%m%d').date()
    user = User.query.filter_by(lineid=event.line_id).one()
    mailer.send_mail_with_csv(user, csv, target_date)
    event.send_thank_msg()


def construct_csv(menu_q: Menu) -> str:
    first_column = [menu_q.category] + menu_q.description.split('\n')
    second_column = [''] + menu_q.cycle.split('\n')
    record_q = Record.query.filter_by(menuid=menu_q.menuid).order_by(Record.recordid).all()

    data = [first_column, second_column] + [record_in_linear_list(rec) for rec in record_q]
    transposed = [',,'.join(x) for x in zip_longest(*data, fillvalue='')]
    csv = '\r\n'.join(transposed)
    return csv


def record_in_linear_list(record: Record) -> list:
    rec_list = [record.swimmer]
    style_separator = '|'
    row_separator = '_'
    raw_text = record.times

    # fly,0:28.52 → fly,0:28.52
    # 0:28.52 → ,0:28.52
    pre_insert_comma = lambda x: x if ',' in x else ',' + x

    # スタイルを含む場合は二列分確保する
    if style_separator in raw_text:
        raw_text_no_pipe = raw_text.replace(style_separator, ',')
        time_list_not_aligned = raw_text_no_pipe.split(row_separator)
        time_list_aligned = [pre_insert_comma(time) for time in time_list_not_aligned]
        rec_list = [',' + record.swimmer]
        rec_list.extend(time_list_aligned)
        return rec_list

    else:
        time_list = raw_text.split(row_separator)
        rec_list.extend(time_list)
        return rec_list


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
