# タイム一覧表示でタイムがないときに表示するもの
# 静的

dic = {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "タイムがまだ記録されてません（;≧-≦）",
        "size": "xs",
        "weight": "bold",
        "align": "center"
      }
    ],
    "paddingAll": "md"
  }
}
