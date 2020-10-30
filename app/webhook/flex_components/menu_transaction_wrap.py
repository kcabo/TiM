# タイム一覧と一緒に送られるメニュー削除・変更のUI
# 改変部:
# menu_baseをdic["body"]["contents"][1]["contents"][0]に組み込む
# Variable * 3

dic = {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "2020.10.13 火", # Variable
        "weight": "bold",
        "color": "#4f4f4f",
        "align": "center",
        "offsetBottom": "xs"
      },
      {
        "type": "box",
        "layout": "vertical",
        "contents": [ # ここにmenu_base入る
          {
            "type": "separator"
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
                    "text": "消去",
                    "color": "#F6839C",
                    "weight": "bold"
                  }
                ],
                "height": "40px",
                "justifyContent": "center",
                "alignItems": "center",
                "action": {
                  "type": "postback",
                  "data": "caution=45" # Variable
                }
              },
              {
                "type": "separator"
              },
              {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "text",
                    "text": "変更",
                    "color": "#37D1F9",
                    "weight": "bold"
                  }
                ],
                "justifyContent": "center",
                "alignItems": "center",
                "height": "40px",
                "action": {
                  "type": "uri",
                  "uri": "http://linecorp.com/" # Variable
                }
              }
            ]
          }
        ],
        "backgroundColor": "#ffffff",
        "cornerRadius": "lg"
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
