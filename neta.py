import random

symbols = "🇦🇧🇨🇩🇪🇫🇬🇭🇮🇯🇰🇱🇲🇳🇴🇵🇶🇷🇸🇹🇺🇻🇼🇽🇾🇿"

def pop_regional_indicator(text):
    random.seed(text)
    strings = symbols[random.randint(0,25)] + symbols[random.randint(0,25)]
    # code_list = [ord(c) for c in text]
    # strings = symbols[sum(code_list)%26] + symbols[(sum(code_list)//26)%26]
    if strings == "🇯🇵":
        return strings + ' ←おめでとう！日本だ！'
    else:
        return strings

def random_sticker():
    package = random.randint(11537,11540)
    if package == 11537:
        sticker = random.randint(52002734,52002774)
    elif package == 11538:
        sticker = random.randint(51626494,51626534)
    elif package == 11539:
        sticker = random.randint(52114110,52114150)
    return {"type": "sticker", "packageId": package, "stickerId": sticker}
