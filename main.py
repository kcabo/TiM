from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy

import os
import json
import lineapi
import valueconv
import blockhandler

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
    time_string = db.Column(db.String(40))
    style = db.Column(db.String(40))

class Block(db.Model):
    __tablename__ = "block"
    keyid = db.Column(db.Integer, primary_key=True)
    blockid = db.Column(db.Integer, unique = True)
    date = db.Column(db.Integer)
    category = db.Column(db.String(40))
    description = db.Column(db.String(100))
    cycle = db.Column(db.String(40))

@app.route("/create")
def create_db():
    db.create_all()
    return "ok"

@app.route("/")
def test():
    # q = UserStatus.query.filter_by(keyid = 1).first()
    # if q == None:
    #     print("nnnon")
    # else:
    #     print(q.lineid)
    #     q.authorized = True
    #     db.session.add(q)
    #     db.session.commit()
    pass
    return "ok"

@app.route("/callback", methods=['POST'])
def callback():

    body = request.get_data(as_text=True)
    body_json = json.loads(body)

    for event in body_json['events']:

        try:
            reply_token = event['replyToken']
        except:
            print("リプライトークンの取得に失敗しました。") #おそらくブロックされたとき
            continue

        event_type = event['type']
        lineid = event['source']['userId']

        user = UserStatus.query.filter_by(lineid = lineid).first()
        if user == None:
            lineapi.SendTextMsg(reply_token,["登録されていないユーザーです。"])
            continue
        elif user.authorized != True:
            lineapi.SendTextMsg(reply_token,["許可されていないユーザーです。"])
            continue

        if event_type == "follow": #友だち追加ならユーザーテーブルに追加
            name = lineapi.GetProfile(lineid)
            reg = UserStatus(lineid = lineid, name = name, authorized = True, status = "add", currentblock = "190521")

            try:    #lineidにunique制約あるので二重登録しようとするとエラー発生
                db.session.add(reg)
                db.session.commit()
                lineapi.SendTextMsg(reply_token,["おｋ"])
            except:
                lineapi.SendTextMsg(reply_token,["登録に失敗しました。","既に登録されている可能性がございます。"])

        elif event_type == "postback": #ボタン押したときとかのポストバックイベント
            p_data = event['postback']['data']
            print(p_data)

        elif event_type == "message": #普通にメッセージきたとき
            msg_type = event['message']['type']
            if msg_type == "text":
                msg_text = event['message']['text']

                #timedataテーブルに新しい記録を追加する
                if msg_text.find("\n") > 0: #改行が含まれるときは登録と判断
                    rows = msg_text.split("\n")
                    swimmer = rows[0]
                    currentblock = user.currentblock
                    if currentblock == "":
                        lineapi.SendTextMsg(reply_token,["一覧からブロックを選択してから入力してください。"])
                        continue

                    for i, row in enumerate(rows):
                        if i != 0: #０個目は名前が書いてあるから飛ばす
                            td = TimeData()
                            td.blockid = currentblock
                            td.row = i
                            td.swimmer = swimmer
                            r = valueconv.RowSeparator(row)
                            td.style = r.style
                            if r.data.isdecimal(): #データ部分が数字のみならタイムを変換
                                time_string = valueconv.fix_time_string(r.data) #ただの整数列を0:00.00の形式にする
                                td.time_string = time_string
                            else:
                                td.time_string = r.data
                            db.session.add(td)

                    try:
                        db.session.commit()
                        lineapi.SendTextMsg(reply_token,["おｋ"])
                    except:
                        lineapi.SendTextMsg(reply_token,["登録に失敗しました。"])

                #ブロック一覧を表示する
                elif msg_text == "一覧":
                    user.currentblock = ""
                    user.status = "add"
                    db.session.add(user)
                    db.session.commit()
                    block_int = blockhandler.BlockDate() #190521
                    block_min = block_int * 10 -1 #1905209
                    block_max = block_int * 10 + 10 #1905220

                    blocks = Block.query.filter_by(blockid = 1905221).all()
                    print(blocks[0].blockid)
                    con = blockhandler.BlocksFlex(blocks)
                    lineapi.SendFlexMsg(reply_token,con,"現在利用可能なブロック一覧だよ～")



    return "ok"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
