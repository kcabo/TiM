from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy

import os
import json
import time
#
# import lineapi
# import valueconv
# import blockhandler
# import csvmail

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #これ書かないとログがうるさくなる
db = SQLAlchemy(app)

#以下DBのテーブルの定義
class UserStatus(db.Model):
    __tablename__ = "userstatus"
    id = db.Column(db.Integer, primary_key = True)
    lineid = db.Column(db.String(), unique = True, nullable = False)
    name = db.Column(db.String())
    authorized = db.Column(db.Boolean, nullable = False)
    status = db.Column(db.String())
    date = db.Column(db.Integer, nullable = False) #20190902
    serial = db.Column(db.Integer, nullable = False) #1

class Record(db.Model):
    __tablename__ = "record"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Integer, nullable = False) #20190902
    serial = db.Column(db.Integer, nullable = False) #1
    swimmer = db.Column(db.String()) #神崎
    times = db.Column(db.String())  #0:29.47,1:01.22,,0:32.43,1:11.44
    styles = db.Column(db.String()) #fr,,fr,,

class Menu(db.Model):
    __tablename__ = "menu"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Integer, nullable = False) #20190902
    serial = db.Column(db.Integer, nullable = False) #1
    category = db.Column(db.String())
    description = db.Column(db.String())
    cycle = db.Column(db.String())

class Event():
    def __init__(event):
        type = event['type']
        if type in ["message","postback","follow"]:
            reply_token = event['replyToken']
            lineid = event['source']['userId']

            if type == "message":
                msg_type = event['message']['type']

                if msg_type == "text":
                    msg_text = event['message']['text']


@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    body_json = json.loads(body)

    for event in body_json['events']:
        event_type = event['type']
        if event_type in ["message","postback","follow"]:
            reply_token = event['replyToken']
            lineid = event['source']['userId']

            if event_type == "message":
                msg_type = event['message']['type']

                if msg_type == "text":
                    msg_text = event['message']['text']
