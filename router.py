import datetime
import json
import os
import re
import requests

from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy

import flexDesigner as flex
import neta
import emailAgent

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #これ書かないとログがうるさくなる
db = SQLAlchemy(app)

access_token = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
headers =  {'Content-Type': 'application/json', 'Authorization' : 'Bearer ' + access_token}


class User(db.Model):
    __tablename__ = "users"
    keyid = db.Column(db.Integer, primary_key = True)
    lineid = db.Column(db.String(), unique = True, nullable = False)
    name = db.Column(db.String(), nullable = False)
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
    swimmer = db.Column(db.String(), nullable = False) #神崎
    times = db.Column(db.String(), nullable = False)  #0:29.47,1:01.22,,0:32.43,1:11.44
    styles = db.Column(db.String(), nullable = False) #fr,,fr,,

    def __init__(self, text, date, sequence):
        rows = text.split('\n')
        self.swimmer = rows[0]
        data_list = [RowParser(row) for row in rows[1:]] #二行目以降をパース タイムとスタイルが１セットになって入っている

        self.times = ','.join([d.time for d in data_list])
        self.styles = ','.join([d.style for d in data_list])
        self.parsed = self.swimmer + '\n' + '\n'.join([d.parsed for d in data_list])
        self.date = date
        self.sequence = sequence

    def set_data_list(self):
        self.time_list = self.times.split(',')
        self.style_list = self.styles.split(',')

    def revert_origin_text(self):
        self.set_data_list()
        origin_times = [fmt.replace(':','').replace('.','') for fmt in self.time_list]
        # スタイルが指定されていないならタイムのみ、されてたら半角スペースでつなげる
        text_array = [t if s == '' else s+' '+t for s,t in zip(self.style_list, origin_times)]
        return self.swimmer + '\n' + '\n'.join(text_array)


    def export_matrix(self):
        self.set_data_list()
        base_val = [0] + list(map(fmt_to_val, self.time_list))
        w = list(map(lambda x: int(x>0), base_val)) #ラップインジケータ。weightのw

        for i in range(1,len(base_val)):
            if w[i]==1 and w[i-1]>0:
                if base_val[i] - base_val[i-1] > 2200: #前のタイムとの差が22秒以上
                    w[i] = w[i-1] + 1

        matrix = []
        if self.styles.replace(',','') != '':
            matrix += [[''] + self.style_list]

        prior_time = [''] + list(map(lambda x: ' ' + x, self.time_list)) #頭に半角つける
        prior_time[0] = self.swimmer
        matrix += [prior_time]

        if max(w) >= 2: #50mごとのラップ
            lap = [0 if weight < 2 else base_val[i]-base_val[i-1] for i, weight in enumerate(w)]
            matrix += [list(map(val_to_efmt, lap))]
            if max(w) >= 4: #100mごとのラップ
                lap = [0 if weight==0 or weight % 2 > 0 else base_val[i]-base_val[i-2] for i, weight in enumerate(w)]
                matrix += [list(map(val_to_efmt, lap))]
                if max(w) >= 6: #200mごとのラップ
                    lap = [0 if weight==0 or weight % 4 > 0 else base_val[i]-base_val[i-4] for i, weight in enumerate(w)]
                    matrix += [list(map(val_to_efmt, lap))]
                    if max(w) >= 10: #400mごとのラップ
                        lap = [0 if weight==0 or weight % 8 > 0 else base_val[i]-base_val[i-8] for i, weight in enumerate(w)]
                        matrix += [list(map(val_to_efmt, lap))]

        matrix += [['']]

        return matrix


    def one_record_flex_content(self):
        self.set_data_list()
        # スタイルが指定されていないならタイムのみ、されてたら半角スペースでつなげる
        text_array = [t if s == '' else s+' '+t for s,t in zip(self.style_list, self.time_list)]
        text = self.swimmer + '\n' + '\n'.join(text_array)

        content = {
          "type": "text",
          "text": text,
          "wrap": True,
          "align": "center",
          "size": "xxs",
          "gravity": "top",
          "action": {
            "type": "postback",
            # "data": "rc_{}_{}_{}".format(self.date, self.sequence, self.swimmer)
            "data": "rc_".format(self.keyid)
            }
        }
        return content

fmt_ptn = re.compile('([0-9]{1,2}):([0-9]{2}).([0-9]{2})') #15分とかのときは：の前は2文字になる
def fmt_to_val(fmt):
    match = re.match(fmt_ptn, fmt)
    if match is None: #コロンを持たないごめんなさいなどの文字列
        return 0
    else:
        min = int(match.group(1))
        sec = int(match.group(2)) * 100 + int(match.group(3))
        return min * 6000 + sec #100倍した秒数

def val_to_efmt(val):
    if val == 0:
        return ''
    else:
        min = str(val // 6000)
        sec = str(val % 6000).zfill(4) #0000
        return " {0}:{1}.{2}".format(min, sec[:2], sec[2:]) #Excelで開いたときに文字列と認識されるよう頭に半角スペース入れる


#50mfr 3245 とかの文字列ならgroup1に50mfr 、group2にfr、group3に3245がマッチする。かっこが3つあることに注意
#つまりgroup2は使用しない
#ごめんなさいはgroup3にのみマッチ
row_ptn = re.compile("(.*(fr|fly|ba|br|IM|im|FR|MR|pull|kick|Fr|Fly|Ba|Br|Pull|Kick|m|ｍ) ?)?(.*$)")
class RowParser:
    def __init__(self, row):
        match = re.match(row_ptn, row)
        raw_time = match.group(3)
        if raw_time.isdecimal():
            self.time = self.format_time(raw_time)
        else: #ごめんなさいのときは変換しないでそのまま
            self.time = raw_time

        if match.group(1) is not None: #スタイルありの行
            self.style = match.group(1).replace(' ','')
            self.parsed = self.style + ' ' + self.time
        else: #10233とかの文字列のときgroup1はNone
            self.style = ''
            self.parsed = self.time

    def format_time(self, string):
        zero_fixed = string.zfill(5) #最小５文字でゼロ埋め 00000
        return "{0}:{1}.{2}".format(zero_fixed[:-4], zero_fixed[-4:-2], zero_fixed[-2:])



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



class Event:
    def __init__(self, event):
        self.event_type = event.get('type')
        self.reply_token = event.get('replyToken')
        self.lineid = event.get('source',{'userId':None}).get('userId')#sourceキーが存在しないとき、NoneからuserIdを探すとエラー
        self.msg_type = event.get('message',{'type':None}).get('type')
        self.text = event.get('message',{'text':''}).get('text','').replace(",","､") #replaceで通常のコンマを､(HALFWIDTH IDEOGRAPHIC COMMA)に置換している
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
        menu_query = Menu.query.filter_by(date = chain_date).order_by(Menu.sequence).all()
        #その日のメニューがなかったとき、Noneのままではリスト内包表記できない
        flex_msg = flex.design_flex_menu_list(str(chain_date), menu_query if menu_query is not None else [])
        self.send_flex(flex_msg, 'MenuList')
        self.user.set_value(date = chain_date, sequence = 0, status = '')


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
                e.show_menu_list(int(chain_date))


            elif e.text == '確認':
                if e.user.sequence == 0:
                    e.send_text('メニューが選択されていません。')
                    e.user.set_value(status = '')
                else:
                    e.show_time_list(e.user.date, e.user.sequence)


            elif e.text == 'メール':
                menu_query = Menu.query.filter_by(date = e.user.date).order_by(Menu.sequence).all()
                if menu_query == []:
                    e.send_text('メールで送るデータがありません')
                else:
                    csv = ''
                    for m in menu_query:
                        record_queries = Record.query.filter_by(date = m.date, sequence = m.sequence).all()
                        record_matrix = [[m.category, m.description], ['',m.cycle]]
                        for r in record_queries:
                            record_matrix += r.export_matrix()

                        #転置先の空白だらけの二次元配列を作成
                        translated = [['']*len(record_matrix) for i in range(len(max(record_matrix, key=len)))]
                        #転置
                        for column, list in enumerate(record_matrix):
                            for i, d in enumerate(list):
                                translated[i][column] = d

                        for row in translated:
                            csv += ','.join(row) + '\n'

                        csv += '..\n'

                    emailAgent.email(e.user, csv)
                    msg_otsukaresama = [{"type": "sticker", "packageId": "11537", "stickerId": "52002734"},
                            {'type' : 'text', 'text' : "メールで送ったよ！ありがとう！おつかれさま！😆😆" }]
                    e.post_reply(msg_otsukaresama)
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

            #タイム登録
            elif e.text.find('\n') > 0:
                if e.user.sequence == 0:
                    e.send_text('メニューが選択されていません。')
                else:
                    record = Record(e.text, e.user.date, e.user.sequence)
                    if Record.query.filter_by(date = e.user.date, sequence = e.user.sequence, swimmer = record.swimmer).first() is None:
                        db.session.add(record)
                        db.session.commit()
                        e.send_text(record.parsed, '登録成功✨')
                    else: #既にその人のデータある時
                        e.send_text('その人のデータは既に存在しています')

            #なんでもない文字列にはネタで返す
            elif e.text != '':
                e.send_text(neta.pop_regional_indicator(e.text))
            else:
                e.post_reply([neta.random_sticker()])

            print(">{}: {}".format(e.user.name, e.text if e.text is not None else e.msg_type).replace('\n',' '))


        #ポストバック処理
        elif e.event_type == 'postback':
            data = e.postback_data.split('_')
            print(f'data:{data}')
            label = data[0]
            date = int(data[1])
            sequence = int(data[2]) if len(data)>2 else None

            if label == 'menu': #"data": "menu_{}".format(prev_date)
                e.show_menu_list(date)

            elif label == 'new': #"data": "new_{}".format(chain_date)
                menu_query = Menu.query.filter_by(date = date).all()
                if len(menu_query)>7:
                    e.send_text('これ以上は新しいメニューは作れません。')
                else:
                    sequence_list = [m.sequence for m in menu_query]
                    new_menu_sequence = max([0] if sequence_list == [] else sequence_list) + 1 #その日のメニューが一つも存在しないとき、新たなシーケンスは１になる
                    new_menu = Menu(date = date, sequence = new_menu_sequence, category = 'category', description = 'description', cycle = 'cycle')
                    db.session.add(new_menu)
                    e.user.set_value(date, new_menu_sequence, 'define')
                    e.send_text("メニューの情報を３行で入力","例：\nSwim\n50*8*1 HighAverage\n1:30")


            elif label == 'edit':
                e.user.set_value(date, sequence, 'define')
                e.send_text("メニューの情報を３行で入力","例：\nSwim\n50*8*1 HighAverage\n1:30")


            #ステータスを変更し、確認メッセージを返す
            elif label == 'kill':
                target_menu = Menu.query.filter_by(date = date, sequence = sequence).first()
                e.user.set_value(date, sequence, 'kill')
                confirm_bubble = flex.design_kill_menu_confirm(target_menu)
                e.send_flex(confirm_bubble, alt_text = 'KillMenu')

            #レコードごとすべてDelete操作する
            elif label == 'yeskill' and e.user.status == 'kill':
                Menu.query.filter_by(date = date, sequence = sequence).delete()
                Record.query.filter_by(date = date, sequence = sequence).delete()
                e.user.set_value(date, 0, '')
                e.send_text('完全に消去しました')

            elif label == 'select':
                e.show_time_list(date, sequence)

            #元の文字列に変換して返す
            elif label == 'rc': # "data": "rc_".format(self.keyid)
                id = data[2]
                target_record = Record.query.filter_by(keyid = id).first()
                origin_text = target_record.revert_origin_text()
                erase_bubble = flex.design_erase_record_bubble(id)
                msgs = [{'type':'text','text':origin_text}] + [{"type":"flex","altText":'EraseRecord', "contents":erase_bubble}]
                e.post_reply(msgs)

            elif label == 'erase': # "data": "erase_{}".format(record_id)
                id = data[2]
                erase_rc = Record.query.filter_by(keyid = id).first()
                e.user.set_value(erase_rc.date, erase_rc.sequence, '')
                swimmer = erase_rc.swimmer
                Record.query.filter_by(keyid = id).delete()
                e.send_text('{}のタイムを削除しました'.format(swimmer))

            print(">{}: {}".format(e.user.name, e.postback_data))
    return '200'




@app.route("/create")
def create_db():
    db.create_all()
    return "CREATED"

@app.route("/delete")
def delete_db():
    TimeData.query.delete()
    db.session.commit()
    return "DELETED"

@app.route("/")
def test():
    return "Home Route"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
