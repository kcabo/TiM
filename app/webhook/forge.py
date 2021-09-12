

def contains_invalid_char(event) -> bool:
    invalid_char = {'|', '_', ':', '.'}
    set_text = set(event.text)
    cross = set_text.intersection(invalid_char)
    if cross:
        retry_msg = f'{cross} を含む記録は登録できません。\n{cross} を別の文字に置き換えて送り直してください'
        event.send_text(retry_msg)
        return False
    else:
        return True


def parse_user_text(event) -> (str, list):
    lines_raw = event.text.split('\n')
    swimmer = lines_raw[0]
    time_lines_raw = lines_raw[1:]
    times_list = [parse_time(raw) for raw in time_lines_raw]

    return swimmer, times_list


def parse_time(raw: str) -> str:
    if ' ' in raw:
        last_space_position = raw.rfind(' ')
        style = raw[:last_space_position]
        time_raw = raw[last_space_position+1:]
        time = format_time(time_raw)
        parsed = f'{style}|{time}'
        return parsed

    else:
        if raw.isdecimal() == False:
            return raw
        else:
            time = format_time(raw)
            return time


def format_time(time_raw: str) -> str:
    fixed = time_raw.zfill(5) #最小５文字でゼロ埋め 00000
    # 6文字の場合もあるため後ろからスライスする
    natural_time = f'{fixed[:-4]}:{fixed[-4:-2]}.{fixed[-2:]}'
    return natural_time
