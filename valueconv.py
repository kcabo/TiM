import  re
# regex = "(fr|fly|ba|br|IM|im|FR|MR|pull|kick|Fr|Fly|Ba|Br|Pull|Kick)*(\w*)"
# 適当な文字列のあとに続くfrやmをスタイルとする
# 冒頭の.*がすべての文字列の意味、つまり200mfrとかはmの文字すらもその中に含まれ(無視されてfrが合致する)、結果的に200mfrが抽出される
regex = ".*(fr|fly|ba|br|IM|im|FR|MR|pull|kick|Fr|Fly|Ba|Br|Pull|Kick|m|ｍ)"
ptn = re.compile(regex)

class RowSeparator():
    def __init__(self, str):
        # match_obj = ptn.mtch(str)
        boundary = 0 #styleの終わる境界 デフォルトは0文字目で終わる＝存在しない
        match_obj = re.search(ptn, str)
        if match_obj is None:
            style = None
        else:
            boundary = match_obj.end() #スタイルと判定された部分が終わる位置
            style = str[:boundary]
        data = str[boundary:]
        if data.isdecimal():  #データ部分が数字のみならタイムを変換
            data = fix_time_string(data)

        self.style = style
        self.data = data

    def merged_data(self):
        if self.style is None:
            merged = self.data
        else:
            merged = self.style + "  " + self.data
        return merged


def fix_time_string(time_int): #ただの整数列を0:00.00の形式にする
    str = time_int.zfill(5) #最小５文字でゼロ埋め
    time_string = "{0}:{1}.{2}".format(str[:-4],str[-4:-2],str[-2:])
    return time_string

# def get_time_value(time_int):
#     minutes = time_int[-6:-4]
#     seconds = int(time_int[-4:]) / 100
#     time_value = 0.0
#
#     if minutes == "":
#         time_value = seconds
#     else:
#         time_value = seconds + int(minutes) * 60
#
#     return time_value
