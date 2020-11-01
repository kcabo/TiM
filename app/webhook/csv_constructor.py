from itertools import zip_longest
from app.models import Record, Menu


def construct_csv(menu_queryies: list) -> str:
    csv_strings = [build_from_menu(menu) for menu in menu_queryies]
    csv = '\r\n.\r\n'.join(csv_strings)
    return csv

def build_from_menu(menu_q: Menu) -> str:
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
