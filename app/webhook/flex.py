import datetime

def build_menus(target_date: datetime.date, menus) -> list:
    menus = {
      "type": "bubble",
      "size": "mega",
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
                  "label": "action",
                  "data": "hello"
                }
              },
              {
                "type": "text",
                "text": "2020.09.12 土",
                "weight": "bold",
                "color": "#4f4f4f",
                "align": "center",
                "flex": 0,
                "gravity": "center",
                "size": "lg",
                "action": {
                  "type": "datetimepicker",
                  "label": "action",
                  "data": "hello",
                  "mode": "date",
                  "max": "2020-09-03",
                  "min": "2020-09-02"
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
                  "label": "action",
                  "data": "hello"
                }
              }
            ],
            "justifyContent": "center",
            "paddingAll": "md",
            "spacing": "md"
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
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                      {
                        "type": "text",
                        "text": "Swim",
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
                    "text": "25*20*2 4t:浮き上がりまで 4t:12.5から 2t:Allout（1sfr 2sS1)",
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
                "text": "1:00",
                "color": "#7F7F7F",
                "gravity": "center",
                "flex": 0,
                "wrap": True,
                "size": "xs"
              }
            ],
            "backgroundColor": "#ffffff",
            "cornerRadius": "lg",
            "paddingAll": "md",
            "paddingEnd": "xxl",
            "action": {
              "type": "postback",
              "label": "action",
              "data": "hello21211"
            }
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
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                      {
                        "type": "text",
                        "text": "Swim",
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
                    "text": "25*20*2 4t:浮き上がりまで 4t:12.5から 2t:Allout（1sfr 2sS1)",
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
                "text": "1:00",
                "color": "#7F7F7F",
                "gravity": "center",
                "flex": 0,
                "wrap": True,
                "size": "xs"
              }
            ],
            "backgroundColor": "#ffffff",
            "cornerRadius": "lg",
            "paddingAll": "md",
            "paddingEnd": "xxl",
            "action": {
              "type": "postback",
              "label": "action",
              "data": "hello21211"
            }
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
            "justifyContent": "center",
            "alignItems": "center",
            "cornerRadius": "40px",
            "height": "50px",
            "action": {
              "type": "uri",
              "label": "action",
              "uri": "http://linecorp.com/"
            },
            "margin": "lg"
          }
        ],
        "paddingAll": "lg",
        "spacing": "7px"
      },
      "styles": {
        "body": {
          "backgroundColor": "#EFF1F6"
        }
      }
    }
    return [menus]
