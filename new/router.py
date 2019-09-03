from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy

import datetime
import os
import json
import time
import requests

import flex_constructor as flex

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
    email = db.Column(db.String())
    status = db.Column(db.String())
    date = db.Column(db.Integer, nullable = False) #190902
    serial = db.Column(db.Integer, nullable = False) #1

class Record(db.Model):
    __tablename__ = "record"
    keyid = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Integer, nullable = False) #190902
    serial = db.Column(db.Integer, nullable = False) #1
    swimmer = db.Column(db.String()) #神崎
    times = db.Column(db.String())  #0:29.47,1:01.22,,0:32.43,1:11.44
    styles = db.Column(db.String()) #fr,,fr,,

class Menu(db.Model):
    __tablename__ = "menu"
    keyid = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Integer, nullable = False) #190902
    serial = db.Column(db.Integer, nullable = False) #1
    category = db.Column(db.String(), nullable = False)
    description = db.Column(db.String(), nullable = False)
    cycle = db.Column(db.String(), nullable = False)


class Event():
    def __init__(event):
        self.event_type = event.get('type')
        self.reply_token = event.get('replyToken')
        self.lineid = event.get('source',{'userId':None}).get('userId')#sourceキーが存在しないとき、NoneからuserIdを探すとエラー
        self.msg_type = event.get('message',{'type':None}).get('type')
        self.text = event.get('message',{'text':None}).get('text')
        self.postback_data = event.get('postback',{'data':None}).get('data')
        self.user = User.query.filter_by(lineid = lineid).first()

    def post_reply(msg_list):
        data = {'replyToken': self.reply_token, 'messages': msg_list}
        requests.post(reply_url, headers=headers, data=json.dumps(data))

    def send_text(*texts):
        msgs = [{'type':'text','text':t} for t in texts]
        post_reply(msgs)

    def send_flex(flex, alt_text = 'Msg'):
        msgs = [{"type":"flex","altText": alt_text,"contents": flex}]
        post_reply(msgs)

    def show_menu_list(chain_date): #190902がchain_date
        menu_query = Menu.query.filter_by(date = int(chain_date)).order_by(Menu.serial).all()
        #その日のメニューがなかったとき、Noneのままではリスト内包表記できない
        flex = flex.design_flex_menu_list(chain_date, menu_query if menu_query is not None else [])
        send_flex(flex, 'MenuList')
        self.user.date = int(chain_date)
        self.user.serial = 0
        self.user.status = ""
        db.session.commit()

    def show_time_list(chain_date, serial):
        pass



@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    body_json = json.loads(body) #辞書型に変換

    for event in body_json['events']:
        e = Event(event)

        #アクセス管理
        if e.user is None:
            e.send_text("不正なアクセスを検知しました。あなたの情報は管理者へ送信されます。")
            print('>Invalid User: {}'.format(e.lineid))
            continue

        #送信文字列処理
        if e.event_type == 'message':

            if e.text == '一覧':
                chain_date = datetime.date.today().strftime('%Y%m%d')
                show_menu_list(chain_date)

            elif e.text == '確認':
                if e.user.serial == 0:
                    e.send_text('メニューが選択されていません。')

                else:
                    pass



            print(">{}: {}".format(e.user.name, e.text if e.text is not None else e.msg_type))

        elif e.event_type == 'postback':
            data = e.postback_data.split('_')

            if data[0] = 'menu':
                show_menu_list(data[1])


@app.route("/create")
def create_db():
    db.create_all()
    return "all tables have just created successfully!\nやったね！"

@app.route("/wake")
def wakeup():
    print("awake")
    return "起きてます"

@app.route("/delete")
def delete_db():
    TimeData.query.delete()
    db.session.commit()
    return "deleted"

@app.route("/")
def test():
    return "This is a test route."

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
