# メニュー一覧の全体レイアウト
# 改変部:
# Variable * 5

dic = {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "text",
            "text": "　◀　",
            "color": "#4f4f4f",
            "flex": 0,
            "gravity": "center",
            "action": {
              "type": "postback",
              "data": "date=201012" # Variable
            }
          },
          {
            "type": "text",
            "text": "2020.10.13 火", # Variable
            "weight": "bold",
            "color": "#4f4f4f",
            "align": "center",
            "flex": 0,
            "gravity": "center",
            "size": "lg",
            "action": {
              "type": "datetimepicker",
              "data": "picker=0",
              "mode": "date",
              "initial":"2020-10-13" # Variable
            }
          },
          {
            "type": "text",
            "text": "　▶　",
            "color": "#4f4f4f",
            "flex": 0,
            "gravity": "center",
            "action": {
              "type": "postback",
              "data": "date=201014" # Variable
            }
          }
        ],
        "justifyContent": "center",
        "paddingAll": "md",
        "spacing": "md"
      },
      {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "＋",
            "size": "3xl",
            "color": "#ffffff",
            "weight": "bold"
          }
        ],
        "background": {
          "type": "linearGradient",
          "angle": "135deg",
          "startColor": "#38E6FA",
          "endColor": "#3477F3"
        },
        "cornerRadius": "30px",
        "height": "50px",
        "action": {
          "type": "uri",
          "uri": "http://linecorp.com/" # Variable
        },
        "margin": "lg",
        "alignItems": "center",
        "justifyContent": "center"
      }
    ],
    "paddingAll": "lg",
    "spacing": "md"
  },
  "styles": {
    "body": {
      "backgroundColor": "#EFF1F6"
    }
  }
}
