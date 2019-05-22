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
    status = db.Column(db.String(40))
    currentblock = db.Column(db.String(40))

@app.route("/create")
def create_db():
    db.create_all()
    return "ok"

@app.route("/callback", methods=['POST'])
def callback():

    body = request.get_data(as_text=True)
    body_json = json.loads(body)

    for event in body_json['events']:
        event_type = event['type']
        if event_type == "follow":
            reply_token = event['replyToken']
            lineid = event['source']['userId']
            name = linepost.GetProfile(lineid)
            reg = UserStatus(lineid = lineid, name = name, status = "add", currentblock = "190521")

            try:
                db.session.add(reg)
                db.session.commit()
                linepost.SendReplyMsg(reply_token,["おｋ"])
            except:
                linepost.SendReplyMsg(reply_token,["登録に失敗しました。","既に登録されている可能性がございます。"])


    return "ok"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
