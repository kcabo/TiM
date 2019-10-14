import json
import os
import random
import requests

symbols = "🇦🇧🇨🇩🇪🇫🇬🇭🇮🇯🇰🇱🇲🇳🇴🇵🇶🇷🇸🇹🇺🇻🇼🇽🇾🇿"
talk_api_url = 'https://api.a3rt.recruit-tech.co.jp/talk/v1/smalltalk'

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
    package = random.randint(11537,11539)
    if package == 11537:
        sticker = random.randint(52002734,52002773)
    elif package == 11538:
        sticker = random.randint(51626494,51626533)
    elif package == 11539:
        sticker = random.randint(52114110,52114149)
    return {"type": "sticker", "packageId": package, "stickerId": sticker}


def a3rt_talk_api(text):
    r = requests.post(talk_api_url, {'apikey': os.environ['A3RT_APIKEY'], 'query': text})
    data = r.json()
    if data['status'] == 0: #正常応答
        return data['results'][0]['reply']
    else:
        return data['message']
