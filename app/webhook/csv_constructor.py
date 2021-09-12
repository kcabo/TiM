import re
from itertools import zip_longest
from app.models import Record, Menu

# CSV内での改行コードはCRLF
# めちゃくちゃだあ

def construct_csv(menu_queryies: list) -> str:
    csv_strings = [build_from_menu(menu) for menu in menu_queryies]
    csv = '\r\n.\r\n'.join(csv_strings)
    return csv


def build_from_menu(menu_q: Menu) -> str:
    descriptions = menu_q.description.split('\n')
    cycles = menu_q.cycle.split('\n')

    records = Record.query.filter_by(menuid=menu_q.menuid).order_by(Record.recordid).all()

    needed_lines = calc_lines_of_matrix(records, descriptions, cycles)

    first_column = [menu_q.category, *descriptions]
    second_column = ['', *cycles]

    only_time_list_square = [record_in_linear_list(rec, needed_lines) for rec in records]
    transposed = [',,'.join(x) for x in zip(*only_time_list_square)]

    print()
    lines_with_menu = [','.join(x) for x in zip_longest(first_column, second_column, transposed, fillvalue='')]
    csv = '\r\n'.join(lines_with_menu)
    return csv


def calc_lines_of_matrix(records, descriptions, cycles) -> int:
    # メニュー表示に必要な行数 Categoryの一行下から始まるため、+1
    menu_lines = max(len(descriptions), len(cycles)) + 1

    # アンダーバーを最も多く含む(必要行数の多い)記録はどれか
    times = map(lambda x: x.times, records)
    times_with_most_bar = max(times, key=lambda x: x.count('_'))

    # このメニューを表にする時に必要な行数を見積もる
    # 'hoge_piyo'ならバー数は1、行数は2
    # 加えて一行目に名前が入る
    # したがってアンダーバーの数にプラス2したものが必要な行数
    needed_lines_unreliable = times_with_most_bar.count('_') + 2

    # メニュー表示に必要な行数を下回っていないか確認する
    needed_lines_reliable = max(
        needed_lines_unreliable,
        menu_lines
    )

    return needed_lines_reliable


def _record_in_linear_list(record: Record) -> list:
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


def record_in_linear_list(record: Record, needed_lines: int) -> list:
    style_separator = '|'
    line_separator = '_'
    raw_text = record.times
    if style_separator in raw_text:
        time_list_untouch = raw_text.split(line_separator)
        time_list = []
        style_list = []
        for line in time_list_untouch:
            if style_separator in line:
                style, time = line.split(style_separator)
            else:
                time = line
                style = ''
            time_list.append(time)
            style_list.append(style)

    else:
        time_list = raw_text.split(line_separator)
        style_list = []

    return export_matrix(record.swimmer, time_list, style_list, needed_lines)


# 以下レガシーコードの流用
def export_matrix(swimmer, time_list, style_list, needed_lines):
    base_val = [0] + list(map(fmt_to_val, time_list))
    w = list(map(lambda x: int(x>0), base_val)) #ラップインジケータ。weightのw

    for i in range(1,len(base_val)):
        if w[i]==1 and w[i-1]>0:
            if base_val[i] - base_val[i-1] > 2200: #前のタイムとの差が22秒以上
                w[i] = w[i-1] + 1

    matrix = []
    if style_list:
        matrix += [[''] + style_list]

    prior_time = [''] + list(map(lambda x: ' ' + x, time_list)) #頭に半角つける
    prior_time[0] = swimmer
    matrix += [prior_time]

    if max(w) >= 2: #50mごとのラップ
        lap = [0 if weight < 2 else base_val[i]-base_val[i-1] for i, weight in enumerate(w)]
        matrix += [list(map(val_to_efmt, lap))]
        if max(w) >= 4: #100mごとのラップ
            lap = [0 if weight==0 or weight % 2 > 0 else base_val[i]-base_val[i-2] for i, weight in enumerate(w)]
            matrix += [list(map(val_to_efmt, lap))]
            if max(w) >= 6: #200mごとのラップ
                lap = [0 if weight==0 or weight % 4 > 0 else base_val[i]-base_val[i-4] for i, weight in enumerate(w)]
                matrix += [list(map(val_to_efmt, lap))]
                if max(w) >= 10: #400mごとのラップ
                    lap = [0 if weight==0 or weight % 8 > 0 else base_val[i]-base_val[i-8] for i, weight in enumerate(w)]
                    matrix += [list(map(val_to_efmt, lap))]

    # matrix += [['']]
    # return matrix
    width = len(matrix)

    matrix_proper = [','.join(line) for line in zip_longest(*matrix, fillvalue='')]
    gap = max(needed_lines - len(matrix_proper), 0)
    matrix_proper.extend([','*(width-1)] * gap)
    return matrix_proper


fmt_ptn = re.compile('([0-9]{1,2}):([0-9]{2}).([0-9]{2})') #15分とかのときは：の前は2文字になる
def fmt_to_val(fmt):
    match = re.match(fmt_ptn, fmt)
    if match is None: #コロンを持たないごめんなさいなどの文字列
        return 0
    else:
        min = int(match.group(1))
        sec = int(match.group(2)) * 100 + int(match.group(3))
        return min * 6000 + sec #100倍した秒数


def val_to_efmt(val):
    if val == 0:
        return ''
    else:
        min = str(val // 6000)
        sec = str(val % 6000).zfill(4) #0000
        return " {0}:{1}.{2}".format(min, sec[:2], sec[2:]) #Excelで開いたときに文字列と認識されるよう頭に半角スペース入れる
