import datetime

def menu_box(chain_date, serial, description, category_and_cycle): #ひとつのメニューの四角い部分
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
            "width": "20px",
            "backgroundColor": "#26408B"
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
            "backgroundColor": "#A6CFD5",
            "margin": "md",
            "action": {
              "type": "postback",
              "label": "kill",
              "data": "kill_{}_{}".format(chain_date, serial)
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
            "backgroundColor": "#A6CF44",
            "action": {
              "type": "postback",
              "label": "edit",
              "data": "edit_{}_{}".format(chain_date, serial)
          }
          }
        ],
        "height": "60px",
        "borderColor": "#eeeeee",
        "borderWidth": "1px",
        "action": {
          "type": "postback",
          "label": "select",
          "data": "select_{}_{}".format(chain_date, serial)
        }
      }

    return box


def design_flex_menu_list(chain_date, menu_query):
    date = datetime.datetime.strptime(chain_date, '%y%m%d')
    prev_date = (date - datetime.timedelta(days=1)).strftime('%y%m%d')
    next_date = (date + datetime.timedelta(days=1)).strftime('%y%m%d')

    menu_list_contents = [menu_box(chain_date, m.serial, m.description, m.category + " " + m.cycle) for m in menu_query]

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
        "borderColor": "#eeeeee",
        "borderWidth": "1px",
        "backgroundColor": "#26408B",
        "action": {
          "type": "postback",
          "label": "new_menu",
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
              "label": "prev_date",
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
              "label": "next_date",
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
