import datetime

def FlexMsg():
    contents = {
      "type": "bubble",
      "body": {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "text",
            "text": "かんざき,"
          },
          {
            "type": "text",
            "text": "flex!"
          }
        ]
      }
    }
    return contents


# print(datetime.date.today())
