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