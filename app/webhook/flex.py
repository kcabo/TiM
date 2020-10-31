import datetime
from copy import deepcopy

from app.webhook import flex_components as components

layer_capacity = 4

def build_menus(target_date: datetime.date, queries) -> dict:
    # TODO: メニュー作成URLを指定
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
    cnt_records = len(record_queries)

    if cnt_records == 0:
        return components.no_records

    cnt_needed_layers = (cnt_records - 1) // layer_capacity + 1
    bubble_capacity = 3
    bubbles = []
    tmp_contents = []

    iter = yield_layer(record_queries)
    for idx_layer, layer in enumerate(iter, 1): # idxは1からはじまる
        tmp_contents.append(layer)
        tmp_contents.append({"type": "separator"})

        # バブルをひとつ作る
        # 一つのバブルに3層溜まった or 最後の層
        if idx_layer % bubble_capacity == 0 or idx_layer == cnt_needed_layers:
            bubble = deepcopy(components.times_wrap)
            bubble["body"]["contents"] = tmp_contents[:-1]
            bubbles.append(bubble)
            tmp_contents = []

    # バブル一つ分で済む量ならカルーセルにはしない
    if cnt_records <= 12:
        return bubbles[0]

    # 複数のバブルを送るため、カルーセルにまとめる
    else:
        carousel = {
          "type": "carousel",
          "contents": bubbles
        }
        return carousel


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


def yield_layer(record_queries: list) -> dict:
    # 受け取ったRecordのリストを4つずつchunkに分ける
    # 一段ごとパーツ(FlexUI)を返す
    max_index = len(record_queries)
    for idx in range(0, max_index, layer_capacity):
        start = idx
        end = idx + layer_capacity # max_indexを超えることがあるが問題ない
        chunk = record_queries[start:end]
        cells = [build_record_cell(record) for record in chunk]
        layer = build_record_layer(cells)
        yield layer


def build_record_cell(rec_q) -> dict:
    cell = deepcopy(components.record_cell)

    chained_time_no_pipe = rec_q.times.replace('|', ' ')
    time_list = chained_time_no_pipe.split('_')
    text = '\n'.join([rec_q.swimmer] + time_list)

    cell["text"] = text
    cell["action"]["data"] = f'rec={rec_q.recordid}'
    return cell


def build_record_layer(record_cells: list) -> dict:
    # record_cellsは1~4の長さを持つリスト
    layer = deepcopy(components.times_layer)
    for i, cell in enumerate(record_cells):
        layer["contents"][i] = cell
    return layer
