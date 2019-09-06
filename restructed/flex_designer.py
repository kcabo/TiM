import datetime


def menu_box(chain_date, sequence, description, category_and_cycle): #ひとつのメニューの四角い部分
    box = {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "filler"
              }
            ],
            "width": "5px",
            "backgroundColor": "#004385"
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "text",
                "text": description,
                "flex": 4,
                "size": "xxs",
                "gravity": "bottom",
                "wrap": True
              },
              {
                "type": "text",
                "text": category_and_cycle,
                "flex": 4,
                "size": "xxs",
                "color": "#bbbbbb"
              }
            ],
            "margin": "xl"
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "filler"
              },
              {
                "type": "text",
                "text": "Kill",
                "size": "xs",
                "align": "center",
                "weight": "bold",
                "color": "#ffffff"
              },
              {
                "type": "filler"
              }
            ],
            "width": "50px",
            "backgroundColor": "#BCE784",
            "margin": "md",
            "action": {
              "type": "postback",
              "data": "kill_{}_{}".format(chain_date, sequence)
            }
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "filler"
              },
              {
                "type": "text",
                "text": "Edit",
                "size": "xs",
                "align": "center",
                "weight": "bold",
                "color": "#ffffff"
              },
              {
                "type": "filler"
              }
            ],
            "width": "50px",
            "backgroundColor": "#5DD39E",
            "action": {
              "type": "postback",
              "data": "edit_{}_{}".format(chain_date, sequence)
          }
          }
        ],
        "height": "60px",
        "borderColor": "#dddddd",
        "borderWidth": "1px",
        "action": {
          "type": "postback",
          "data": "select_{}_{}".format(chain_date, sequence)
        }
      }

    return box


def design_flex_menu_list(chain_date, menu_query):
    date = datetime.datetime.strptime(chain_date, '%y%m%d')
    prev_date = (date - datetime.timedelta(days=1)).strftime('%y%m%d')
    next_date = (date + datetime.timedelta(days=1)).strftime('%y%m%d')

    menu_list_contents = [menu_box(chain_date, m.sequence, m.description, m.category + " " + m.cycle) for m in menu_query]

    new_menu_box =   {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "filler"
          },
          {
            "type": "text",
            "text": "NEW MENU",
            "size": "lg",
            "align": "center",
            "weight": "bold",
            "color": "#ffffff"
          },
          {
            "type": "filler"
          }
        ],
        "height": "60px",
        "borderColor": "#dddddd",
        "borderWidth": "1px",
        "backgroundColor": "#004385",
        "action": {
          "type": "postback",
          "data": "new_{}".format(chain_date)
        }
      }

    menu_list_contents.append(new_menu_box)

    menu_list = {
      "type": "bubble",
      "size": "giga",
      "header": {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "text",
                "text": "◀",
                "color": "#ffffff",
                "size": "3xl",
                "weight": "bold",
                "gravity": "center",
                "align": "start",
                "flex": 5
              }
            ],
            "action": {
              "type": "postback",
              "data": "menu_{}".format(prev_date)
            }
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "text",
                "text": date.strftime('%m/%d(%a)'),
                "color": "#ffffff",
                "size": "xxl",
                "flex": 5,
                "weight": "bold",
                "gravity": "center",
                "align": "center"
              }
            ],
            "flex": 5
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "text",
                "text": "▶",
                "color": "#ffffff",
                "size": "3xl",
                "weight": "bold",
                "gravity": "center",
                "align": "end",
                "flex": 5
              }
            ],
            "action": {
              "type": "postback",
              "data": "menu_{}".format(next_date)
            }
          }
        ],
        "paddingAll": "20px",
        "backgroundColor": "#0367D3",
        "height": "100px",
        "paddingTop": "22px"
      },
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": menu_list_contents,
        "spacing": "md"
      }
    }

    return menu_list


def design_flex_record_list_bubble(record_queries, menu_query): #最大12 つまりひとつのバブルを返す関数 1行につき4人で最大3行

    filler = {"type": "filler"}
    separator = {"type": "separator"}

    count_record = len(record_queries)
    count_needed_rows = (count_record-1)//4 + 1 #たとえば5人分のタイムなら2行必要となる

    fixed_record_array = [record.one_record_flex_content() for record in record_queries]

    #たとえば5人分のタイムなら2行つかって8人分のスペースがある→ あいている3人分をfillerで埋める
    fixed_record_array.extend([filler for i in range(count_needed_rows*4 - count_record)])

    body_contents = []

    for i in range(count_needed_rows): #0~2

        one_row = {
          "type": "box",
          "layout": "horizontal",
          "contents": fixed_record_array[i*4:(i+1)*4] #0~3,4~7,8~11を順にリストで取り出す
        }

        body_contents.append(one_row)

        if i != count_needed_rows -1: #最終行でないならセパレーターを入れる
            body_contents.append(separator)


    record_bubble = {
      "type": "bubble",
      "header": {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "text",
            "text": menu_query.format_date(if_twolines = True),
            "size": "sm",
            "flex": 2,
            "color": "#ffffff",
            "align": "center",
            "weight": "bold",
            "wrap": True,
            "gravity": "center"
          },
          {
            "type": "separator",
            "color": "#ffffff"
          },
          {
            "type": "text",
            "text": menu_query.format_menu_3_row(),
            "size": "xxs",
            "flex": 3,
            "color": "#ffffff",
            "wrap": True
          }
        ],
        "backgroundColor": "#0367D3",
        "spacing": "xl"
      },
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": body_contents,
        "spacing": "lg"
      }
    }

    return record_bubble

def design_kill_menu_confirm(menu_information):
    confirm_bubble = {
      "type": "bubble",
      "size": "kilo",
      "body": {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "separator",
            "color": "#c82333"
          },
          {
            "type": "text",
            "text": menu_information,
            "wrap": True,
            "size": "xs",
            "flex": 5
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "filler"
              },
              {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "filler"
                  },
                  {
                    "type": "text",
                    "text": "消去",
                    "align": "center",
                    "weight": "bold",
                    "color": "#c82333"
                  },
                  {
                    "type": "filler"
                  }
                ],
                "borderColor": "#c82333",
                "cornerRadius": "4px",
                "borderWidth": "1px",
                "height": "30px"
              },
              {
                "type": "filler"
              }
            ],
            "flex": 3
          }
        ],
        "spacing": "xl"
      }
    }
    return confirm_bubble
