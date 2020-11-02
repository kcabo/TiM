import datetime

from app.models import db, Menu, Record, User
from app.webhook import flex, mailer, forge
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


def add_new_record(event):
    menu_q = fetch_current_menu(event)
    if menu_q is None: return None
    if forge.is_text_appropriate(event) == False: return None

    lines_raw = event.text.split('\n')
    swimmer = lines_raw[0]
    time_lines_raw = lines_raw[1:]

    try:
        time_lines_fixed = [forge.parse_time(raw) for raw in time_lines_raw]
    except forge.TooManySpaces as e:
        error_msg = e.args[0]
        event.send_text(error_msg, '一行につきスペースは一つにしてください')
        return None

    times = '_'.join(time_lines_fixed)
    new_record = Record(menu_q.menuid, swimmer, times)
    db.session.add(new_record)
    db.session.commit()

    repeat_with_pipe = '\n'.join([swimmer, *time_lines_fixed])
    repeat = repeat_with_pipe.replace('|', ' ')
    event.send_text(repeat, '登録成功✨')


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


def pick_record(event, record_id: int):
    target_record = Record.query.get(record_id)
    if target_record is None:
        event.send_text('記録が見つかりませんでした...')
        return None
    primitive_text = revert_to_primitive_text(target_record)
    delrec_button = flex.build_delete_record_button(target_record.recordid)

    primitive_text_wrap = {
        "type": "text",
        "text": primitive_text
    }
    delrec_button_wrap = {
        "type": "flex",
        "altText": 'この記録を削除',
        "contents": delrec_button
    }
    event.reply([primitive_text_wrap, delrec_button_wrap])


def revert_to_primitive_text(record: Record) -> str:
    style_separator = '|'
    line_separator = '_'
    time_text = record.times
    time_text_multi_line = time_text. \
        replace(':',''). \
        replace('.',''). \
        replace(style_separator, ' '). \
        replace(line_separator, '\n')
    swimmer = record.swimmer
    primitive_text = f'{swimmer}\n{time_text_multi_line}'
    return primitive_text


def delete_record(event, record_id: int):
    target_record = Record.query.get(record_id)
    if target_record is None:
        event.send_text('記録が見つかりませんでした...')
        return None
    swimmer = target_record.swimmer
    db.session.delete(target_record)
    db.session.commit()
    event.send_text(f'{swimmer}のタイムを削除したよ！')


def ask_whether_delete_menu(event, menu_id: int):
    target_menu = Menu.query.get(menu_id)
    if target_menu is None:
        event.send_text('メニューが見つかりませんでした...')
        return None
    count_records = Record.query.filter_by(menuid=menu_id).count()
    flex_menu_caution = flex.build_delete_menu_caution(target_menu, count_records)

    alt_text = 'メニューを消去しますか？'
    event.send_flex(alt_text, [flex_menu_caution])
    event.aim_menu_id(menu_id)


def delete_menu(event, menu_id: int):
    current_menu = event.menu_id
    if current_menu != menu_id:
        event.send_text('もう一度メニューを選択し直してください')
        return None

    count_deleted_menu = Menu.query.filter_by(menuid=menu_id).delete()
    count_deleted_rec = Record.query.filter_by(menuid=menu_id).delete()
    db.session.commit()
    event.send_text(f'{count_deleted_menu}個のメニューと{count_deleted_rec}件のタイムを完全に消去しちゃいました')

# with open('de.py', 'w', encoding='UTF8') as f:
#     import json
#     print(json.dumps(flex_menu_transaction), file=f)
