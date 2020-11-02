# メニューを削除するかどうかの確認
# 改変部:
# menu_baseをdic["body"]["contents"][1]に組み込む
# Variable * 4

dic = {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "2020.09.12 土", # Variable
        "weight": "bold",
        "color": "#4f4f4f",
        "align": "center",
        "offsetBottom": "xs"
      },
      {
        # ここにmenu_base入る
      },
      {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "本当にこのメニューを消去しますか？",
            "size": "xs",
            "align": "center",
            "color": "#7F7F7F",
            "weight": "bold"
          },
          {
            "type": "text",
            "text": "このメニューに含まれる21個のタイムも削除されます", # Variable
            "size": "xxs",
            "align": "center",
            "color": "#7F7F7F"
          },
          {
            "type": "box",
            "layout": "horizontal",
            "contents": [
              {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "text",
                    "text": "キャンセル",
                    "weight": "bold"
                  }
                ],
                "alignItems": "center",
                "justifyContent": "center",
                "width": "120px",
                "height": "36px",
                "backgroundColor": "#E7E6E6",
                "cornerRadius": "sm",
                "action": {
                  "type": "postback",
                  "data": "cancel=45", # Variable
                  "displayText": "キャンセル"
                }
              },
              {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "text",
                    "text": "消去",
                    "weight": "bold",
                    "color": "#ffffff"
                  }
                ],
                "alignItems": "center",
                "justifyContent": "center",
                "width": "120px",
                "height": "36px",
                "backgroundColor": "#C00000",
                "cornerRadius": "sm",
                "action": {
                  "type": "postback",
                  "data": "delmenu=45", # Variable
                  "displayText": "消去"
                }
              }
            ],
            "margin": "lg",
            "justifyContent": "space-around"
          }
        ],
        "margin": "lg"
      }
    ],
    "paddingAll": "lg"
  },
  "styles": {
    "body": {
      "backgroundColor": "#EFF1F6"
    }
  }
}
