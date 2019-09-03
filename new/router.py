from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy

import os
import json
import time
import requests

# import api_adaptor as api
#
# import lineapi
# import valueconv
# import blockhandler
# import csvmail

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #これ書かないとログがうるさくなる
db = SQLAlchemy(app)

access_token = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
headers =  {
    'Content-Type': 'application/json',
    'Authorization' : 'Bearer ' + access_token
}
reply_url = 'https://api.line.me/v2/bot/message/reply'


#以下DBのテーブルの定義
class User(db.Model):
    __tablename__ = "users"
    keyid = db.Column(db.Integer, primary_key = True)
    lineid = db.Column(db.String(), unique = True, nullable = False)
    name = db.Column(db.String())
    authorized = db.Column(db.Boolean, nullable = False)
    status = db.Column(db.String())
    date = db.Column(db.Integer, nullable = False) #20190902
    serial = db.Column(db.Integer, nullable = False) #1

class Record(db.Model):
    __tablename__ = "record"
    keyid = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Integer, nullable = False) #20190902
    serial = db.Column(db.Integer, nullable = False) #1
    swimmer = db.Column(db.String()) #神崎
    times = db.Column(db.String())  #0:29.47,1:01.22,,0:32.43,1:11.44
    styles = db.Column(db.String()) #fr,,fr,,

class Menu(db.Model):
    __tablename__ = "menu"
    keyid = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Integer, nullable = False) #20190902
    serial = db.Column(db.Integer, nullable = False) #1
    category = db.Column(db.String())
    description = db.Column(db.String())
    cycle = db.Column(db.String())


class Event():
    def __init__(event):
        self.event_type = event.get('type')
        self.reply_token = event.get('replyToken')
        self.lineid = event.get('source',{'userId':None}).get('userId')#sourceキーが存在しないとき、NoneからuserIdを探すとエラー
        self.msg_type = event.get('message',{'type':None}).get('type')
        self.text = event.get('message',{'text':None}).get('text')
        self.user = User.query.filter_by(lineid = lineid).first()

    def post_reply(msg_list):
        data = {'replyToken': self.reply_token, 'messages': msg_list}
        requests.post(reply_url, headers=headers, data=json.dumps(data))

    def send_text(*texts):
        msgs = [{'type':'text','text':t} for t in texts]
        post_reply(msgs)


@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    body_json = json.loads(body) #辞書型に変換

    for event in body_json['events']:

        e = Event(event)

        #アクセス管理
        if e.user == None:
