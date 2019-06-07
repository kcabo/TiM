from datetime import datetime,timedelta

def BlockDate():
    now = datetime.now()
    # date_str = "2019/5/20 06:30" #デバッグ用
    # now = datetime.strptime(date_str, '%Y/%m/%d %H:%M')
    yobi = now.weekday()
    if yobi == 6:
        nominal_time = now - timedelta(hours=24) #日曜日は無条件で土曜日となる
    else:
        nominal_time = now - timedelta(hours=6) #6時間前 つまり次の日の朝６時までは前日のデータを編集できる
    block_int = int(nominal_time.strftime("%y%m%d"))
    return block_int

def BlocksFlex(blocks):
    image_url ="https://lh5.googleusercontent.com/UJ2GhiSGkpLPhoH8VNNLRBz7B-XQlKMkFUruwfp3V04YAOvGooBg0jdDvZpWX3lqmLIYLw"
    bubbles = []
    new_bubble = {
      "type": "bubble",
      "hero": {
        "type": "image",
        "size": "full",
        "aspectRatio": "20:22",
        "aspectMode": "cover",
        "url": image_url,
        "action": {
              "type": "postback",
              "data": "new"
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
    }

    image_url2 = "https://lh3.googleusercontent.com/qrq-d52VAo-GwO5Se9tYw9EgdjYJOr-m6aWvrErVAcDdz242EucZDGUlcCMrdmR1mAysBg"
    if len(blocks) > 0:
        block_date_int = blocks[0].date
        block_date = datetime.strptime(str(block_date_int), "%y%m%d")
        yobi_list = ["月","火","水","木","金","土","日"]
        yobi = yobi_list[block_date.weekday()]
        date_info = "📅 {}月{}日({})".format(block_date.month, block_date.day, yobi)
        for b in blocks:
            bubble_sample = {
              "type": "bubble",
              "hero": {
                "type": "image",
                "size": "full",
                "aspectRatio": "20:7",
                "aspectMode": "cover",
                "url": image_url2
              },
              "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                  {
                    "type": "text",
                    "text": "{}　🆔 {}".format(date_info, b.blockid),
                    "wrap": True,
                    "weight": "regular",
                    "size": "sm"
                  },
                  {
                    "type": "text",
                    "text": " " if b.category is None or b.category == "" else b.category,
                    "wrap": True,
                    "weight": "bold",
                    "size": "md",
                    "margin": "md"
                  },
                  {
                    "type": "text",
                    "text": " " if b.description is None or b.description == "" else b.description,
                    "wrap": True,
                    "weight": "bold",
                    "size": "sm",
                    "margin": "none"
                  },
                  {
                    "type": "text",
                    "text": " " if b.cycle is None or b.cycle == "" else b.cycle,
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
                    "color": "#006699",
                    "height": "sm",
                    "action": {
                      "type": "postback",
                      "label": "ブロックごと削除する",
                      "data": "delete_{}".format(b.blockid)
                    }
                  },
                  {
                    "type": "button",
                    "style": "primary",
                    "color": "#006699",
                    "height": "sm",
                    "action": {
                      "type": "postback",
                      "label": "見出しを編集する",
                      "data": "header_{}".format(b.blockid)
                    }
                  },
                  {
                    "type": "button",
                    "style": "primary",
                    "color": "#1d366d",
                    "action": {
                      "type": "postback",
                      "label": "✨このブロックに切り替える✨",
                      "data": "switch_{}".format(b.blockid)
                    }
                  }
                ]
              }
            }

            bubbles.append(bubble_sample)
    bubbles.append(new_bubble)
    contents = {"type": "carousel", "contents": bubbles}
    return contents


def get_time_data_all_list(data):
    list = []
    buf_l = []
    for d in data:
        if d.row == 1: #１行目なら前の選手のバッファデータを全部listに加えて、次の選手に備える
            if len(buf_l) > 0:
                list.append("\n".join(buf_l))
            buf_l = [d.swimmer]
        if d.style is None: #スタイルとデータをあわせたやつをバッファに格納（バッファはリストに加えるときに改行で分ける）
            buf_l.append(d.data)
        else:
            buf_l.append(d.style + "　" + d.data)
    list.append("\n".join(buf_l)) #最後の選手だけバッファ内に残ってるから最後にもっかいリストに加える
    return list


def all_data_content_flex(block, row_integrated_list):
    body_contents = [{
        "type": "text",
        "text": "ID:{}".format(block.blockid),
        "size": "lg",
        "weight": "bold"
      },
      {
          "type": "text",
          "text": "{}\n{}\n{}".format(block.category,block.description,block.cycle),
          "wrap": True,
          "size": "xxs",
          "weight": "bold"
        }]

    separator = {
      "type": "separator",
      "margin": "md"
    }

    #バブルは最大サイズ10KB カルーセルは50KBらしい
    last_index = len(row_integrated_list) - 1
    three_swimmers_contents = []
    for i, str in enumerate(row_integrated_list):
        if str == "":
            continue
        one_swimmer_data = {
          "type": "box",
          "layout": "vertical",
          "spacing": "md",
          "contents": [
            {
              "type": "text",
              "text": str,
              "wrap": True,
              "size": "xxs",
              "align": "center",
            },
            {
              "type": "button",
              "style": "primary",
              "color": "#2e6095",
              "height": "sm",
              "action": {
                "type": "postback",
                "label": "削除",
                "data": "remove_{}_{}".format(block.blockid, str.split("\n")[0]),
              }
            }
          ]
        }
        three_swimmers_contents.append(one_swimmer_data)

        #なぜかーうまくーこれがー動かないー →うごいたあああああ
        if i == last_index:
            filled = len(three_swimmers_contents)
            filler = {
              "type": "box",
              "layout": "vertical",
              "spacing": "md",
              "contents": [{"type": "text","text": " ",}]
            }
            if filled != 3:
                for j in range(3 - filled):
                    three_swimmers_contents.append(filler)

        if i % 3 == 2 or i == last_index: #horizontalブロックにおいて三個目のとき。いっぱいなので次のブロックに行く。最後の要素のときも残った文追加しておしまい
            three_swimmers = {
              "type": "box",
              "layout": "horizontal",
              "spacing": "lg",
              "contents": three_swimmers_contents
              }
            #three_swimmersとseparatorは並立関係。どちらも同じ階層のコンテンツに配列として格納される
            body_contents.append(separator)
            body_contents.append(three_swimmers)
            three_swimmers_contents = [] #また一個目から格納し直す

    msg = {
      "type": "flex",
      "altText": "入力したタイムの一覧",
      "contents": {
        "type": "bubble",
        "body": {
          "type": "box",
          "layout": "vertical",
          "spacing": "md",
          "contents": body_contents
        }
      }
    }
    return msg


#ごめん、これより下はスパゲッティ ぶっちゃけあんまいじりたくない
def confirm_flex_data_remove(blockid, swimmer):
    contents = {
      "type": "bubble",
      "body": {
        "type": "box",
        "layout": "vertical",
        "spacing": "lg",
        "contents": [
          {
            "type": "text",
            "text": "本当に{}の記録を削除しますか？".format(swimmer),
            "wrap": True,
            "size": "md"
          },
          {
            "type": "box",
            "layout": "horizontal",
            "spacing": "lg",
            "contents": [
              {
                "type": "button",
                "style": "link",
                "color": "#9a073c",
                "height": "sm",
                "action": {
                  "type": "postback",
                  "label": "削除する",
                  "data": "rmconfirm_{}_{}".format(blockid,swimmer)
                }
              },
              {
                "type": "button",
                "style": "link",
                "color": "#1d366d",
                "height": "sm",
                "action": {
                  "type": "postback",
                  "label": "キャンセル",
                  "data": "rmconfirm_no"
                }
              }
            ]
          }
        ]
      }
    }


    return contents

def get_all_contents_in_text(block, data): #これだととんでもない長さになるから使ってない アルゴリズム自体は他の関数に応用
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
