# タイム削除ボタン
# 改変部:
# Variable * 1

dic = {
  "type": "bubble",
  "size": "nano",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "この記録を削除",
            "weight": "bold",
            "color": "#C00000",
            "size": "xs",
            "align": "center"
          }
        ],
        "borderColor": "#C00000",
        "cornerRadius": "sm",
        "borderWidth": "normal",
        "action": {
          "type": "postback",
          "data": "delrec=42", # Variable
          "displayText": "削除"
        },
        "paddingTop": "md",
        "paddingBottom": "md"
      }
    ],
    "paddingAll": "md"
  }
}
