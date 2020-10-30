import datetime
from copy import deepcopy

from app.webhook import flex_components as components


def build_menus(target_date: datetime.date, queries) -> dict:
    # TODO: アクションを指定 メニュー作成URLを指定
    embedded_menu_cards = [
        build_menu_base_card(menu_query, button=True) for menu_query in queries
    ]

    menu_wrap = deepcopy(components.menu_wrap)

    today_japanese = date_jpn_period_chain(target_date)
    today_hyphenated = target_date.strftime('%Y-%m-%d')
    yesterday = target_date - datetime.timedelta(days=1)
    tomorrow = target_date + datetime.timedelta(days=1)
    yesterday_int = int(yesterday.strftime('%y%m%d'))
    tomorrow_int = int(tomorrow.strftime('%y%m%d'))

    menu_wrap["body"]["contents"][0]["contents"][0]["action"]["data"] = f'date={yesterday_int}'
    menu_wrap["body"]["contents"][0]["contents"][2]["action"]["data"] = f'date={tomorrow_int}'
    menu_wrap["body"]["contents"][0]["contents"][1]["text"] = today_japanese
    menu_wrap["body"]["contents"][0]["contents"][1]["action"]["initial"] = today_hyphenated

    if embedded_menu_cards:
        # contents内の二個目以降の要素として組み込み挿入
        index = 1
        menu_wrap["body"]["contents"][index:index] = embedded_menu_cards

    return menu_wrap


def build_menu_transaction(menu_query) -> dict:
    # TODO: メニュー編集URLを指定
    card = build_menu_base_card(menu_query)

    date_int = menu_query.date
    target_date = datetime.datetime.strptime(str(date_int), '%y%m%d')
    menu_transaction_wrap = deepcopy(components.menu_transaction_wrap)
    menu_transaction_wrap["body"]["contents"][0]["text"] = date_jpn_period_chain(target_date)
    menu_transaction_wrap["body"]["contents"][1]["contents"][-1]["contents"][0]["action"]["data"] = f'caution={menu_query.menuid}'

    menu_transaction_wrap["body"]["contents"][1]["contents"][0:0] = [card]
    return menu_transaction_wrap


def build_records_scroll(record_queries: list) -> dict:
    return  {
      "type": "bubble",
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "2020.10.13 火", # Variable
            "weight": "bold",
            "color": "#4f4f4f",
            "align": "center",
            "offsetBottom": "xs"
          }]
         }
         }


def date_jpn_period_chain(target_date: datetime.date) -> str:
    # 2020.09.12 土
    period_chain = target_date.strftime('%Y.%m.%d')
    week_num = target_date.weekday()
    youbi = ['月', '火', '水', '木', '金', '土', '日'][week_num]
    return f'{period_chain} {youbi}'


def build_menu_base_card(menu_query, button=False) -> dict:
    # 辞書型はミュータブルのため、別々のインスタンスを複製する
    # copyをしないと単一のグローバルなmenu_base変数にアクセスしてしまう
    card = deepcopy(components.menu_base)

    # 空白文字だった場合は空白を補足
    # 空白文字をFlexで送信できないため
    card["contents"][0]["contents"][0]["contents"][0]["text"] = menu_query.category or ' '
    card["contents"][0]["contents"][1]["text"] = menu_query.description or ' '
    card["contents"][1]["text"] = menu_query.cycle or ' '

    if button:
        card["action"] = {
          "type": "postback",
          "data": f"menu={menu_query.menuid}"
        }
    return card
