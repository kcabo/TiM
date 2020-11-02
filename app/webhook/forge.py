

def is_text_appropriate(event) -> bool:
    invalid_char = {'|', '_', ':', '.'}
    text = event.text
    set_text = set(text)
    cross = set_text.intersection(invalid_char)
    if cross:
        retry_msg = f'{cross} を含む記録は登録できません。\n{cross} を別の文字に置き換えて送り直してください'
        event.send_text(retry_msg)
        return False
    else:
        return True


def parse_time(raw: str) -> str:
    if ' ' in raw:
        count_space = raw.count(' ')
        if count_space > 1:
            raise TooManySpaces(f'スペースが多すぎます({count_space}個)')
        style, time_raw = raw.split(' ')
        time = format_time(time_raw)
        parsed = f'{style}|{time}'
        return parsed

    else:
        if raw.isdecimal() == False:
            return raw
        time = format_time(raw)
        return time


class TooManySpaces(Exception):
    pass


def format_time(time_raw: str) -> str:
    fixed = time_raw.zfill(5) #最小５文字でゼロ埋め 00000
    # 6文字の場合もあるため後ろからスライスする
    natural_time = f'{fixed[:-4]}:{fixed[-4:-2]}.{fixed[-2:]}'
    return natural_time
