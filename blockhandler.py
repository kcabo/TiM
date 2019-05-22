from datetime import datetime,timedelta

def BlockDate():
    now = datetime.now()
    # date_str = "2019/5/20 06:30" #デバッグ用
    # now = datetime.strptime(date_str, '%Y/%m/%d %H:%M')
    yobi = now.weekday()
    if yobi == 6 or yobi == 2: #月が0で日が6 水日は時間帯にかかわらず全日を参照
        nominal_time = now - timedelta(hours=24)
    else:
        nominal_time = now - timedelta(hours=7)
    block_int = int(nominal_time.strftime("%y%m%d"))
    return block_int



def BlocksFlex(blocks, block_date):
    if len(blocks) == 0:
        object = block_date * 10 + 1
    else:
        object = blocks[-1].blockid + 1

    action_new = {"method": "new", "object": str(object)}
    bubbles = [{
      "type": "bubble",
      "hero": {
        "type": "image",
        "size": "full",
        "aspectRatio": "20:20",
        "aspectMode": "cover",
        "url": "https://drive.google.com/uc?export=view&id=1TJf3oWXtG4BF9VpqAxTb9qzAoMkO2u_K",
        "action": {
              "type": "postback",
              "data": action_new
            }
      },
      "footer": {
        "type": "box",
        "layout": "vertical",
        "spacing": "sm",
        "contents": [
          {
            "type": "text",
            "text": "<新規作成は上の画像をタップ>",
            "wrap": True,
            "weight": "regular",
            "size": "xs",
            "align": "center",
            "color": "#999999"
          }
        ]
      }
    }]
    print(bubbles)
    if len(blocks) > 0:
        for b in blocks:
            bubble_sample = {
              "type": "bubble",
              "hero": {
                "type": "image",
                "size": "full",
                "aspectRatio": "20:7",
                "aspectMode": "cover",
                "url": "https://drive.google.com/uc?export=view&id=11O6iLjfxVbag2sAP3k93C9AkS_qygU0Y"
              },
              "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                  {
                    "type": "text",
                    "text": "BlockID:{}".format(b.blockid),
                    "wrap": True,
                    "weight": "regular",
                    "size": "md"
                  },
                  {
                    "type": "text",
                    "text": "Swim",
                    "wrap": True,
                    "weight": "bold",
                    "size": "md",
                    "margin": "md"
                  },
                  {
                    "type": "text",
                    "text": "50*4*1 high average",
                    "wrap": True,
                    "weight": "bold",
                    "size": "sm",
                    "margin": "none"
                  },
                  {
                    "type": "text",
                    "text": "1:00",
                    "wrap": True,
                    "weight": "bold",
                    "size": "sm",
                    "margin": "none"
                  }
                ]
              },
              "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                  {
                    "type": "button",
                    "style": "primary",
                    "color": "#2e6095",
                    "action": {
                      "type": "postback",
                      "label": "編集",
                      "data": "受け取れこの文字列を"
                    }
                  },
                  {
                    "type": "button",
                    "style": "primary",
                    "color": "#1d366d",
                    "action": {
                      "type": "postback",
                      "label": "確認",
                      "data": "こっちは下のだ"
                    }
                  }
                ]
              }
            }

            bubbles.append(bubble_sample)

    contents = {"type": "carousel", "contents": bubbles}
    print(bubbles,"2")
    return contents


# print(datetime.date.today())
