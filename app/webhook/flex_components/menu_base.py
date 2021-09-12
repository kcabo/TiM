# メニュー一覧、タイム一覧、メニュー削除時に使用するメニューのレイアウト
# 改変部:
# true -> True
# Variable * 3
# このdic直下にactionキーが指定されることがある


dic = {
  "type": "box",
  "layout": "horizontal",
  "contents": [
    {
      "type": "box",
      "layout": "vertical",
      "contents": [
        {
          "type": "box",
          "layout": "vertical",
          "contents": [
            {
              "type": "text",
              "text": "Swim", # Variable
              "color": "#ffffff",
              "size": "xs",
              "weight": "bold",
              "adjustMode": "shrink-to-fit"
            }
          ],
          "backgroundColor": "#37D1F9",
          "cornerRadius": "xxl",
          "alignItems": "center",
          "width": "75px",
          "paddingAll": "xs"
        },
        {
          "type": "text",
          "text": "50*4*1 allout!", # Variable
          "weight": "bold",
          "wrap": True,
          "size": "xs",
          "margin": "md"
        }
      ],
      "paddingEnd": "lg"
    },
    {
      "type": "text",
      "text": "1:30", # Variable
      "color": "#7F7F7F",
      "gravity": "center",
      "flex": 0,
      "size": "xs",
      "wrap": True
    }
  ],
  "backgroundColor": "#ffffff",
  "cornerRadius": "lg",
  "paddingAll": "md",
  "paddingEnd": "xxl",
}
