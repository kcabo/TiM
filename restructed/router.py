import datetime
import json
import os
import requests

from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy

import flex_designer as flex
import neta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #これ書かないとログがうるさくなる
db = SQLAlchemy(app)

access_token = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
headers =  {
    'Content-Type': 'application/json',
    'Authorization' : 'Bearer ' + access_token
}


#以下DBのテーブルの定義
class User(db.Model):
    __tablename__ = "users"
    keyid = db.Column(db.Integer, primary_key = True)
    lineid = db.Column(db.String(), unique = True, nullable = False)
    name = db.Column(db.String())
    authorized = db.Column(db.Boolean, nullable = False)
    email = db.Column(db.String())
    date = db.Column(db.Integer, nullable = False) #190902
    sequence = db.Column(db.Integer, nullable = False) #1
    status = db.Column(db.String())

    def set_value(self, date = None, sequence = None, status = None):
        if date is not None:
            self.date = date
        if sequence is not None:
            self.sequence = sequence
        if status is not None:
            self.status = status
        db.session.commit()

class Record(db.Model):
    __tablename__ = "record"
    keyid = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Integer, nullable = False) #190902
    sequence = db.Column(db.Integer, nullable = False) #1
    swimmer = db.Column(db.String()) #神崎
    times = db.Column(db.String())  #0:29.47,1:01.22,,0:32.43,1:11.44
    styles = db.Column(db.String()) #fr,,fr,, or None

    def __init__(self, text, date, sequence):
        rows = text.split('\n')
        self.swimmer = rows[0]
        self.times = ','.join(rows[1:])
        self.date = date
        self.sequence = sequence

    def one_record_flex_content(self):
        if self.styles is None:
            text = self.swimmer + "\n" + self.times.replace(',','\n')
        else:
            time_array = self.times.split(',')
            style_array = self.styles.split(',')
            # スタイルが指定されていないならタイムのみ、されてたら半角スペースでつなげる
            text_array = [t if s == '' else s+' '+t for s,t in zip(style_array, time_array)]
            text_array.insert(0, self.swimmer)
            text = '\n'.join(text_array)

        content = {
          "type": "text",
          "text": text,
          "wrap": True,
          "align": "center",
          "size": "xxs",
          "action": {
            "type": "postback",
            "data": "rc_{}_{}_{}".format(self.date, self.sequence, self.swimmer)
            }
        }
        return content


class Menu(db.Model):
    __tablename__ = "menu"
    keyid = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Integer, nullable = False) #190902
    sequence = db.Column(db.Integer, nullable = False) #1
    category = db.Column(db.String(), nullable = False)
    description = db.Column(db.String(), nullable = False)
    cycle = db.Column(db.String(), nullable = False)

    def define_menu(self,category,description,cycle):
        self.category = category
        self.description = description
        self.cycle = cycle

    def datetime_object(self):
        return datetime.datetime.strptime(str(self.date),"%y%m%d")

    def format_date(self, if_twolines): #'09/02\n(Mon)を返す'
        obj = self.datetime_object()
        if if_twolines:
            return obj.strftime('%m/%d\n(%a)')
        else:
            return obj.strftime('%m/%d(%a)')

    def format_menu_3_row(self):
        return self.category + "\n" + self.description + "\n" + self.cycle



class Event():
    def __init__(self, event):
        self.event_type = event.get('type')
        self.reply_token = event.get('replyToken')
        self.lineid = event.get('source',{'userId':None}).get('userId')#sourceキーが存在しないとき、NoneからuserIdを探すとエラー
        self.msg_type = event.get('message',{'type':None}).get('type')
        self.text = event.get('message',{'text':''}).get('text').replace(",","､") #replaceで通常のコンマを､(HALFWIDTH IDEOGRAPHIC COMMA)に置換している
        self.postback_data = event.get('postback',{'data':None}).get('data')
        self.user = User.query.filter_by(lineid = self.lineid).first()

    def post_reply(self, msg_list):
        data = {'replyToken': self.reply_token, 'messages': msg_list}
        requests.post('https://api.line.me/v2/bot/message/reply', headers=headers, data=json.dumps(data))

    def send_text(self, *texts):
        msgs = [{'type':'text','text':t} for t in texts]
        self.post_reply(msgs)

    def send_flex(self, flex_msg, alt_text = 'Msg'):
        msgs = [{"type":"flex","altText": alt_text,"contents": flex_msg}]
        self.post_reply(msgs)


    def show_menu_list(self, chain_date): #190902がchain_date
        menu_query = Menu.query.filter_by(date = int(chain_date)).order_by(Menu.sequence).all()
        #その日のメニューがなかったとき、Noneのままではリスト内包表記できない
        flex_msg = flex.design_flex_menu_list(chain_date, menu_query if menu_query is not None else [])
        self.send_flex(flex_msg, 'MenuList')
        self.user.set_value(date = int(chain_date), sequence = 0, status = '')


    def show_time_list(self, date, sequence):
        record_queries = Record.query.filter_by(date = date, sequence = sequence).all()
        menu_query = Menu.query.filter_by(date = date, sequence = sequence).first()

        count_record = len(record_queries)
        count_needed_bubbles = (count_record-1)//12 + 1 #たとえば15人分のタイムなら2バブル必要となる

        bubbles = []
        for i in range(count_needed_bubbles): #0~
            one_bubble = flex.design_flex_record_list_bubble(record_queries[i*12:(i+1)*12], menu_query)
            bubbles.append(one_bubble)

        if len(bubbles) == 0:
            self.send_text('まだタイムが登録されていません。')
        else:
            carousel = {
                "type": "carousel",
                "contents": bubbles
                }
            self.send_flex(carousel, 'RecordList')
        self.user.set_value(date = date, sequence = sequence, status = '')




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
        # elif e.user.authorized == False:
        #     e.send_text("不正なアクセスを検知しました。あなたの情報は管理者へ送信されます。")
        #     print('>Invalid User: {}'.format(e.lineid))
        #     continue

        #送信文字列処理
        if e.event_type == 'message':

            if e.text == '一覧':
                chain_date = datetime.date.today().strftime('%y%m%d')
                e.show_menu_list(chain_date)

            elif e.text == '確認':
                if e.user.sequence == 0:
                    e.send_text('メニューが選択されていません。')
                    e.user.set_value(status = '')
                else:
                    e.show_time_list(e.user.date, e.user.sequence)

            elif e.text == 'メール':
                e.user.set_value(status = '')

            elif e.text == 'jump':
                e.user.set_value(status = '')

            elif e.user.status == 'define':
                text_array = e.text.split('\n')
                if len(text_array) == 3:
                    current_menu = Menu.query.filter_by(date = e.user.date, sequence = e.user.sequence).first()
                    current_menu.define_menu(text_array[0],text_array[1],text_array[2])
                    e.user.set_value(status = '')
                    e.send_text('メニューの情報を記録しました。タイム入力ができます。')
                else:
                    e.send_text('3行で入力してください。')

            elif e.text.find('\n') > 0:
                if e.user.sequence == 0:
                    e.send_text('メニューが選択されていません。')
                else:
                    record = Record(e.text, e.user.date, e.user.sequence)
                    db.session.add(record)
                    db.session.commit()
                    e.send_text(e.text, '登録完了')

            else:
                e.send_text(neta.pop_regional_indicator(e.text))

            print(">{}: {}".format(e.user.name, e.text if e.text is not None else e.msg_type).replace('\n',' '))


        #ポストバック処理
        elif e.event_type == 'postback':
            data = e.postback_data.split('_')

            if data[0] == 'menu': #"data": "menu_{}".format(prev_date)
                e.show_menu_list(data[1])

            elif data[0] == 'new': #"data": "new_{}".format(chain_date)
                date = int(data[1])
                menu_query = Menu.query.filter_by(date = date).all()
                new_menu_sequence = len(menu_query) + 1
                new_menu = Menu(date = date, sequence = new_menu_sequence, category = 'category', description = 'description', cycle = 'cycle')
                db.session.add(new_menu)
                e.user.set_value(date = date, sequence = new_menu_sequence, status = 'define')
                e.send_text("メニューの情報を３行で入力","例：\nSwim\n50*8*1 HighAverage\n1:30")


            elif data[0] == 'edit': #"data": "edit_{}_{}".format(chain_date, sequence)
                e.user.set_value(date = int(data[1]), sequence = int(data[2]), status = 'define')
                e.send_text("メニューの情報を３行で入力","例：\nSwim\n50*8*1 HighAverage\n1:30")


            elif data[0] == 'kill': #"data": "kill_{}_{}".format(chain_date, sequence)
                date = int(data[1])
                sequence = int(data[2])
                target_menu = Menu.query.filter_by(date = date, sequence = sequence).first()

                if e.user.status == 'kill': #レコードごとすべてDelete操作する
                    Menu.query.filter_by(date = date, sequence = sequence).delete()
                    Record.query.filter_by(date = date, sequence = sequence).delete()
                    e.user.set_value(date = date, sequence = 0, status = '')
                    e.send_text('完全に消去しました')

                else: #ステータスを変更し、確認メッセージを返す
                    e.user.set_value(date = date, sequence = sequence, status = 'kill')
                    confirm_bubble = flex.design_kill_menu_confirm(target_menu)
                    e.send_flex(confirm_bubble, alt_text = 'KillMenu')

            elif data[0] == 'select': #"data": "select_{}_{}".format(chain_date, sequence)
                date = int(data[1])
                sequence = int(data[2])
                e.show_time_list(date, sequence)

            elif data[0] == 'rc': #"data": "rc_{}_{}_{}".format(self.date, self.sequence, self.swimmer)
                if e.user.status == 'erase':
                    pass
                else:
                    pass

            elif data[0] == 'erase':
                date = int(data[1])
                sequence = int(data[2])
                swimmer = data[3]
                Record.query.filter_by(date = date, sequence = sequence, swimmer = swimmer).delete()
                e.user.set_value(date = date, sequence = sequence, status = '')
                e.send_text('{}のタイムを削除しました'.format(swimmer))

    return '200'




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
