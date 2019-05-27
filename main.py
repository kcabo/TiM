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
    currentblock = db.Column(db.Integer)

class TimeData(db.Model):
    __tablename__ = "timedata"
    keyid = db.Column(db.Integer, primary_key=True)
    blockid = db.Column(db.Integer)
    row = db.Column(db.Integer)
    swimmer = db.Column(db.String(40))
    data = db.Column(db.String(40))
    style = db.Column(db.String(40))

class MenuBlock(db.Model):
    __tablename__ = "menublock"
    # keyid = db.Column(db.Integer, primary_key=True)
    blockid = db.Column(db.Integer, primary_key = True)
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
    # if q is None:
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

        if event_type != "follow": #追加時はこの操作はしない
            user = UserStatus.query.filter_by(lineid = lineid).first()
            if user is None:
                lineapi.SendTextMsg(reply_token,["登録されていないユーザーです。"])
                continue
            elif user.authorized != True:
                lineapi.SendTextMsg(reply_token,["許可されていないユーザーです。"])
                continue

        if event_type == "follow": #友だち追加ならユーザーテーブルに追加
            name = lineapi.GetProfile(lineid)
            reg = UserStatus(lineid = lineid, name = name, authorized = True, status = "recruit", currentblock = 0)

            try:    #lineidにunique制約あるので二重登録しようとするとエラー発生
                db.session.add(reg)
                db.session.commit()
                lineapi.SendTextMsg(reply_token,["おｋ"])
            except:
                lineapi.SendTextMsg(reply_token,["登録に失敗しました。","既に登録されている可能性がございます。"])

        elif event_type == "postback": #ボタン押したときとかのポストバックイベント
            p_data = event['postback']['data']
            print(p_data)
            pd = p_data.split("_")

            if pd[0] == "new": #一覧から新規作成を押したとき
                if user.status != "": #最新のカルーセルから新規作成ボタンを押したなら""のはず
                    lineapi.SendTextMsg(reply_token,["もう一度一覧を呼び出してから選択してください。"])
                    continue
                object = pd[1]
                try:
                    mb = MenuBlock()
                    mb.blockid = int(object)
                    mb.date = object[:6] #最初の6文字が日付となってる
                    db.session.add(mb)
                    db.session.commit() #もしすでに登録されているブロックIDを追加しようとしたらエラーになる
                except:
                    lineapi.SendTextMsg(reply_token,["ブロック作成中にエラーが発生しました。\nもう一度一覧から新規作成を試してみてください。"])
                else:
                    user.currentblock = int(object)
                    user.status = "define" #この状態で受け取った文字列はブロック名編集となる
                    db.session.commit()
                    new_block_msg = ["新しいブロックが生成されました。\n例にならってブロックの情報を追加してください。","例：\n--------\nSwim\n50*4*1 HighAverage\n1:00\n--------"]
                    lineapi.SendTextMsg(reply_token,new_block_msg)

            elif pd[0] == "header":
                if user.status != "": #最新のカルーセルから新規作成ボタンを押したなら""のはず
                    lineapi.SendTextMsg(reply_token,["もう一度一覧を呼び出してから選択してください。"])
                    continue
                object = pd[1]
                user.currentblock = int(object)
                user.status = "define" #この状態で受け取った文字列はブロック名編集となる
                db.session.commit()
                lineapi.SendTextMsg(reply_token,["例にならってブロックの情報を上書きしてください。","例：\n--------\nSwim\n50*4*1 HighAverage\n1:00\n--------"])

            elif pd[0] == "switch": #一覧から切り替えを押したとき
                if user.status != "": #最新のカルーセルから新規作成ボタンを押したなら""のはず
                    lineapi.SendTextMsg(reply_token,["もう一度一覧を呼び出してから選択してください。"])
                    continue
                object = pd[1]
                user.currentblock = int(object)
                user.status = "add" #この状態で受け取った文字列は通常のデータ登録となる
                db.session.commit()

                all_data = TimeData.query.filter_by(blockid = int(object)).all()
                switch_block = MenuBlock.query.filter_by(blockid = int(object)).first()
                list = blockhandler.get_all_contents_in_list(all_data)
                msgs = []
                count_data = len(list)
                print(count_data)
                for i in range(count_data // 12 + 1): #データの入っているリストを１２個毎に分割する
                    start = i * 12
                    end = start + 12
                    max_12_list = list[start:end]
                    print(max_12_list)
                    msg = blockhandler.all_data_content_flex(switch_block,max_12_list)
                    msgs.append(msg)
                switch_block_msg = "BlockID:{}に切り替えました。\n編集を開始してください。".format(object)
                msgs.append(switch_block_msg)
                lineapi.versatile_send_msgs(reply_token,msgs)

            elif pd[0] == "delete": #一覧から削除を押したとき
                object = pd[1]
                user.currentblock = int(object)
                user.status = "delete" #この状態から「はい」を選択すると削除となる
                db.session.commit()
                confirm_msg = "本当にBlockID:{}を削除しますか？".format(object)
                con = blockhandler.ConfirmTemplate(confirm_msg)
                lineapi.SendTemplatexMsg(reply_token,con,"確認メッセージ(無視しないでね)")

            elif pd[0] == "confirm": #ブロック削除確認メッセージを選択したとき
                answer = pd[1]
                if user.status != "delete":
                    lineapi.SendTextMsg(reply_token,["過去のボタンは押さないで～"])
                    continue
                if answer == "yes":
                    object = user.currentblock
                    del_block = MenuBlock.query.filter_by(blockid = object).first()
                    del_times = TimeData.query.filter_by(blockid = object).all()
                    try:
                        db.session.delete(del_block)
                        if len(del_times) > 0: #削除するタイムデータが見つかったときのみ削除
                            db.session.delete(del_times)
                        db.session.commit()
                        msg = "削除しました。"
                    except:
                        msg = "削除対象が見つかりませんでした。"
                else:
                    msg = "キャンセルしました。"
                user.currentblock = 0
                user.status = "completed" #ここからだと一覧呼ばないと新規作成できない
                db.session.commit()
                lineapi.SendTextMsg(reply_token,[msg])

            elif pd[0] == "remove": #データ一覧から削除する選手を選択したとき
                lineapi.SendTextMsg(reply_token,[pd[1],pd[2]])

        elif event_type == "message": #普通にメッセージきたとき
            msg_type = event['message']['type']
            if msg_type != "text":
                lineapi.SendTextMsg(reply_token,["(;´･ω･)･･･"])
                continue

            msg_text = event['message']['text']

            #ブロック一覧を表示する ブロックIDとステータスは一覧をみるとリセットされる
            if msg_text == "一覧":
                user.currentblock = 0
                user.status = ""
                db.session.commit()
                block_date = blockhandler.BlockDate() #19052
                blocks = MenuBlock.query.filter_by(date = block_date).order_by(MenuBlock.blockid).limit(9).all()
                print(blocks)
                con = blockhandler.BlocksFlex(blocks,block_date)
                lineapi.SendFlexMsg(reply_token,con,"現在利用可能なブロック一覧だよ～")

            #ブロックのヘッダーステータスを編集する
            elif user.status == "define":
                new_block = MenuBlock.query.filter_by(blockid = user.currentblock).first()
                st_list = msg_text.split("\n")
                if len(st_list) == 3:
                    new_block.category = st_list[0]
                    new_block.description = st_list[1]
                    new_block.cycle = st_list[2]

                    user.status = "add" #ユーザー情報を更新
                    db.session.commit()
                    lineapi.SendTextMsg(reply_token,["新しいブロックが正しく登録されました。\nこのままこのブロックの編集ができます。"])
                else:
                    lineapi.SendTextMsg(reply_token,["なんでもいいから3行で入力してください。"])

            #timedataテーブルに新しい記録を追加する
            elif msg_text.find("\n") > 0: #改行が含まれるときは登録と判断
                rows = msg_text.split("\n")
                swimmer = rows[0]
                currentblock = user.currentblock
                if user.status != "add":
                    lineapi.SendTextMsg(reply_token,["一覧からブロックを選択してから入力してください。"])
                    continue

                already_exists = TimeData.query.filter_by(blockid = currentblock, swimmer = swimmer).first()
                if already_exists != None:
                    lineapi.SendTextMsg(reply_token,["既にその選手のデータは登録されているよん"])
                    continue

                commit_data = [swimmer]
                for i, row in enumerate(rows):
                    if i != 0: #０個目は名前が書いてあるから飛ばす
                        td = TimeData()
                        td.blockid = currentblock
                        td.row = i
                        td.swimmer = swimmer
                        r = valueconv.RowSeparator(row)
                        td.style = r.style
                        td.data = r.data
                        db.session.add(td)
                        commit_data.append(r.merged_data())

                try:
                    db.session.commit()
                    msg = "\n".join(commit_data)
                    lineapi.SendTextMsg(reply_token,[msg,"登録成功！"])
                except:
                    lineapi.SendTextMsg(reply_token,["登録に失敗しました。"])





    return "ok"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
