from datetime import datetime,timedelta

def BlockDate():
    now = datetime.now()
    # date_str = "2019/5/20 06:30" #デバッグ用
    # now = datetime.strptime(date_str, '%Y/%m/%d %H:%M')
    yobi = now.weekday()
    if yobi == 6 or yobi == 2: #月が0で日が6 水日は時間帯にかかわらず前日を参照
        nominal_time = now - timedelta(hours=24)
    else:
        nominal_time = now - timedelta(hours=7)
    block_int = int(nominal_time.strftime("%y%m%d"))
    return block_int

def get_all_contents_in_text(block, data):
    list = []
    buf_l = ["ID:{}\n{}\n{}\n{}".format(block.blockid, block.category, block.description, block.cycle)]
    for d in data:
        if d.row == 1: #１行目なら前の選手のバッファデータを全部listに加えて、次の選手に備える
            list.append("\n".join(buf_l))
            buf_l = [d.swimmer]
        if d.style is None: #スタイルとデータをあわせたやつをバッファに格納（バッファはリストに加えるときに改行で分ける）
            buf_l.append(d.data)
        else:
            buf_l.append(d.style + "　" + d.data)

    list.append("\n".join(buf_l)) #最後の選手だけバッファ内に残ってるから最後にもっかいリストに加える
    msg = "\n-------\n".join(list)
    return msg

def BlocksFlex(blocks, block_date):
    if len(blocks) == 0:
        object = block_date * 100 + 1
    else:
        object = blocks[-1].blockid + 1 #並び替えて一番最後になったブロックのIDが最大

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
              "data": "new_{}".format(str(object))
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
                    "text": "[空欄]" if b.category is None or b.category == "" else b.category,
                    "wrap": True,
                    "weight": "bold",
                    "size": "md",
                    "margin": "md"
                  },
                  {
                    "type": "text",
                    "text":"[空欄]" if b.description is None or b.description == "" else b.description,
                    "wrap": True,
                    "weight": "bold",
                    "size": "sm",
                    "margin": "none"
                  },
                  {
                    "type": "text",
                    "text": "[空欄]" if b.cycle is None or b.cycle == "" else b.cycle,
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
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "lg",
                    "contents": [
                      {
                        "type": "button",
                        "style": "primary",
                        "color": "#2e6095",
                        "action": {
                          "type": "postback",
                          "label": "編集",
                          "data": "header_{}".format(b.blockid)
                        }
                      },
                      {
                        "type": "button",
                        "style": "primary",
                        "color": "#2e6095",
                        "action": {
                          "type": "postback",
                          "label": "削除",
                          "data": "delete_{}".format(b.blockid)
                        }
                      }
                    ]
                  },
                  {
                    "type": "button",
                    "style": "primary",
                    "color": "#1d366d",
                    "action": {
                      "type": "postback",
                      "label": "このブロックに切り替える",
                      "data": "switch_{}".format(b.blockid)
                    }
                  }
                ]
              }
            }

            bubbles.append(bubble_sample)

    contents = {"type": "carousel", "contents": bubbles}

    return contents

def ConfirmTemplate(confirm_msg):
    template = {
      "type": "confirm",
      "text": confirm_msg,
      "actions": [
          {
            "type": "postback",
            "label": "はい",
            "data": "confirm_yes"
          },
          {
            "type": "postback",
            "label": "いいえ",
            "data": "confirm_no"
          }
      ]
      }
    return template
