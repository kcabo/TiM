
symbols = "🇦🇧🇨🇩🇪🇫🇬🇭🇮🇯🇰🇱🇲🇳🇴🇵🇶🇷🇸🇹🇺🇻🇼🇽🇾🇿"

def pop_regional_indicator(text):
    code_list = [ord(c) for c in text]
    return symbols[sum(code_list)%26] + symbols[(sum(code_list)//26)%26]
