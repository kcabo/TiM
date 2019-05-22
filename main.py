from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy

import os
import json
import linepost

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class UserStatus(db.Model):
    __tablename__ = "userstatus"
    keyid = db.Column(db.Integer, primary_key=True)
    # userid = db.Column(db.Integer)
    lineid = db.Column(db.String(100), unique = True)
    name = db.Column(db.String(100))
    authorized = db.Column(db.Boolean)
    status = db.Column(db.String(40))
    currentblock = db.Column(db.String(40))

class TimeData(db.Model):
    __tablename__ = "timedata"
    keyid = db.Column(db.Integer, primary_key=True)
    blockid = db.Column(db.Integer)
    row = db.Column(db.Integer)
    swimmer = db.Column(db.String(40))
    time_value = db.Column(db.String(40))
    style = db.Column(db.String(40))

@app.route("/create")
def create_db():
    db.create_all()
    return "ok"

@app.route("/")
def test():
    q = UserStatus.query.filter_by(keyid = 1).first()
    try:
        print(q.lineid)
    except:
        print("failed")
    return "ok"

@app.route("/callback", methods=['POST'])
def callback():

    body = request.get_data(as_text=True)
    body_json = json.loads(body)

    for event in body_json['events']:
        event_type = event['type']
        reply_token = event['replyToken']
        lineid = event['source']['userId']

        if event_type == "follow": #友だち追加ならユーザーテーブルに追加
            name = linepost.GetProfile(lineid)
            reg = UserStatus(lineid = lineid, name = name, status = "add", currentblock = "190521")

            try:    #lineidにunique制約あるので二重登録しようとするとエラー発生
                db.session.add(reg)
                db.session.commit()
                linepost.SendReplyMsg(reply_token,["おｋ"])
            except:
                linepost.SendReplyMsg(reply_token,["登録に失敗しました。","既に登録されている可能性がございます。"])

        elif event_type == "message": #普通にメッセージきたとき
            msg_type = event['message']['type']
            if msg_type == "text":
                msg_text = event['message']['text']
                if msg_text.find("\n") > 0: #改行が含まれるときは登録と判断
                    rows = msg_text.split("\n")
                    swimmer = rows[0]

                    # currentblock =
                    import valueconv

                    for i, row in enumerate(rows):
                        if i != 0:
                            td = TimeData()
                            td.blockid = 190521
                            td.row = i
                            td.swimmer = swimmer
                            r = valueconv.RowSeparator(row)
                            td.style = r.style
                            if r.data.isdecimal(): #データ部分が数字のみならタイムを変換
                                time_value = valueconv.get_time_value(r.data) #これはfloat型 文字列を秒数にしてる
                                td.time_value = str(time_value)
                            else:
                                td.time_value = r.data
                            db.session.add(td)

                    try:
                        db.session.commit()
                        linepost.SendReplyMsg(reply_token,["おｋ"])
                    except:
                        linepost.SendReplyMsg(reply_token,["登録に失敗しました。"])


    return "ok"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
