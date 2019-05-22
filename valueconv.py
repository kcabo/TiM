import  re

regex = "(fr|fly|ba|br|IM|im|pull|kick|Fr|Fly|Ba|Br|Pull|Kick)*(\w*)"
ptn = re.compile(regex)

class RowSeparator():
    def __init__(self, str):
        match_obj = ptn.match(str)
        self.style = match_obj.group(1)
        self.data = match_obj.group(2)

def get_time_value(time_int):
    minutes = time_int[-6:-4]
    seconds = int(time_int[-4:]) / 100
    time_value = 0.0

    if minutes == "":
        time_value = seconds
    else:
        time_value = seconds + int(minutes) * 60

    return time_value
