import datetime
from copy import deepcopy

from app.webhook import flex_components as components

def int2yobi(week_num: int) -> str:
    return ['月', '火', '水', '木', '金', '土', '日'][week_num]

def build_menus(target_date: datetime.date, queries) -> list:
    # TODO: アクションを指定
    embedded_menus = []
    for menu_q in queries:
        menu = deepcopy(components.menu_base)
        # 空白文字だった場合は空白を補足
        menu["contents"][0]["contents"][0]["contents"][0]["text"] = menu_q.category or ' '
        menu["contents"][0]["contents"][1]["text"] = menu_q.description or ' '
        menu["contents"][1]["text"] = menu_q.cycle or ' '
        embedded_menus.append(menu)

    menu_wrap = deepcopy(components.menu_wrap)

    today_japanese = target_date.strftime('%Y.%m.%d ') + \
        int2yobi(target_date.weekday()) # 2020.09.12 土
    today_hyphenated = target_date.strftime('%Y-%m-%d')
    yesterday = target_date - datetime.timedelta(days=1)
    tomorrow = target_date + datetime.timedelta(days=1)
    yesterday_int = int(yesterday.strftime('%y%m%d'))
    tomorrow_int = int(tomorrow.strftime('%y%m%d'))

    menu_wrap["body"]["contents"][0]["contents"][0]["action"]["data"] = f'date={yesterday_int}'
    menu_wrap["body"]["contents"][0]["contents"][2]["action"]["data"] = f'date={tomorrow_int}'
    menu_wrap["body"]["contents"][0]["contents"][1]["text"] = today_japanese
    menu_wrap["body"]["contents"][0]["contents"][1]["action"]["initial"] = today_hyphenated

    if embedded_menus:
        index = 1
        # contents内の二個目以降の要素として組み込み挿入
        menu_wrap["body"]["contents"][index:index] = embedded_menus

    return [menu_wrap]
