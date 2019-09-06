# import json
# import os
# import requests
#
#
# access_token = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
# headers =  {
#     'Content-Type': 'application/json',
#     'Authorization' : 'Bearer ' + access_token
# }
# reply_url = 'https://api.line.me/v2/bot/message/reply'
#

#
# class Event():
#     def __init__(event):
#         self.event_type = event.get('type')
#         self.reply_token = event.get('replyToken')
#         self.lineid = event.get('source',{'userId':None}).get('userId')#sourceキーが存在しないとき、NoneからuserIdを探すとエラー
#         self.msg_type = event.get('message',{'type':None}).get('type')
#         self.text = event.get('message',{'text':None}).get('text')
#         self.user = User.query.filter_by(lineid = lineid).first()
#
#     def post_reply(msg_list):
#         data = {'replyToken': self.reply_token, 'messages': msg_list}
#         requests.post(reply_url, headers=headers, data=json.dumps(data))
#
#     def send_text(*texts):
#         msgs = [{'type':'text','text':t} for t in texts]
#         post_reply(msgs)

class hoge:
    ho = 3
    def h(a):

        return a + 3
