from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy

import os
import json

import lineapi
import valueconv
import blockhandler
import csvmail

#詳しくはFlaskとsqlalchemyの仕様を読んでください。
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #これ書かないとログがうるさくなる
db = SQLAlchemy(app)

#以下DBのテーブルの定義
class UserStatus(db.Model):
    __tablename__ = "userstatus"
    keyid = db.Column(db.Integer, primary_key = True)
    lineid = db.Column(db.String(100), unique = True, nullable = False)
    name = db.Column(db.String(100))
    authorized = db.Column(db.Boolean, server_default = False)
    status = db.Column(db.String(40))
    currentblock = db.Column(db.Integer)

class TimeData(db.Model):
    __tablename__ = "timedata"
    keyid = db.Column(db.Integer, primary_key=True)
    blockid = db.Column(db.Integer, nullable = False)
    row = db.Column(db.Integer, nullable = False)
    swimmer = db.Column(db.String(40))
    data = db.Column(db.String(40))
    style = db.Column(db.String(40))

class MenuBlock(db.Model):
    __tablename__ = "menublock"
    blockid = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.Integer, nullable = False)
    category = db.Column(db.String(40))
    description = db.Column(db.String(100))
    cycle = db.Column(db.String(40))

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
            name = lineapi.get_line_profile(lineid)
            authorized_flag = True #ここ普段はFalseで
            reg = UserStatus(lineid = lineid, name = name, authorized = authorized_flag, status = "recruit", currentblock = 0)

            try:    #lineidにunique制約あるので二重登録しようとするとエラー発生
                db.session.add(reg)
                db.session.commit()
                lineapi.SendTextMsg(reply_token,["ようこそ{}さん、よろしくおねがいします！🤧🤧".format(name),"あなたのauthorizedステータスは{}です。".format(authorized_flag)])
            except:
                lineapi.SendTextMsg(reply_token,["登録に失敗しました。","既に登録されている可能性がございます。"])


        elif event_type == "postback": #ボタン押したときとかのポストバックイベント
            p_data = event['postback']['data']
            print(p_data)
            pd = p_data.split("_")


            if pd[0] == "new": #一覧から新規作成を押したとき
                block_date = blockhandler.BlockDate() #19052
                blocks = MenuBlock.query.filter_by(date = block_date).order_by(MenuBlock.blockid).all() #今日使ってるブロックを全部持ってくる
                if len(blocks) == 0:
                    new_block_id = block_date * 100 + 1
                else:
                    new_block_id = blocks[-1].blockid + 1 #並び替えて一番最後になったブロックのIDが最大

                try:
                    mb = MenuBlock(blockid = new_block_id, date = block_date)
                    db.session.add(mb)
                    db.session.commit() #もしすでに登録されているブロックIDを追加しようとしたらエラーになる
                except:
                    lineapi.SendTextMsg(reply_token,["ブロック作成中にエラーが発生しました。\nもう一度一覧から新規作成を試してみてください。"])
                else:
                    user.currentblock = new_block_id
                    user.status = "define" #この状態で受け取った文字列はブロック名編集となる
                    db.session.commit()
                    new_block_msg = ["新しいブロックが生成されました。\n例にならってブロックの情報を追加してください。","例：\n--------\nSwim\n50*4*1 HighAverage\n1:00\n--------"]
                    lineapi.SendTextMsg(reply_token,new_block_msg)


            elif pd[0] == "header":
                object = int(pd[1])
                is_it_exist = MenuBlock.query.filter_by(blockid = object).first()
                if is_it_exist == None:
                    lineapi.SendTextMsg(reply_token,["対象のブロックが見つかりません。"])
                    continue
                user.currentblock = object
                user.status = "define" #この状態で受け取った文字列はブロック名編集となる
                db.session.commit()
                lineapi.SendTextMsg(reply_token,["例にならってブロックの情報を上書きしてください。","例：\n--------\nSwim\n50*4*1 HighAverage\n1:00\n--------"])


            elif pd[0] == "switch": #一覧から切り替えを押したとき
                object = int(pd[1])
                is_it_exist = MenuBlock.query.filter_by(blockid = object).first()
                if is_it_exist == None:
                    lineapi.SendTextMsg(reply_token,["対象のブロックが見つかりません。"])
                    continue
                user.currentblock = object
                user.status = "add" #この状態で受け取った文字列は通常のデータ登録となる
                db.session.commit()

                all_data = TimeData.query.filter_by(blockid = object).all()
                switch_block = MenuBlock.query.filter_by(blockid = object).first()
                list = blockhandler.get_all_contents_in_list(all_data)
                msgs = []
                count_data = len(list)
                print("出力するデータ数：{}".format(count_data))
                for i in range(count_data // 12 + 1): #データの入っているリストを１２個毎に分割する
                    start = i * 12
                    end = start + 12
                    max_12_list = list[start:end]
                    print("データリスト：{}".format(max_12_list))
                    msg = blockhandler.all_data_content_flex(switch_block,max_12_list)
                    msgs.append(msg)
                # switch_block_msg = "BlockID:{}に切り替えました。\n編集を開始してください。".format(object)
                # msgs.append(switch_block_msg)
                print(msgs)
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
                    MenuBlock.query.filter_by(blockid = object).delete()
                    TimeData.query.filter_by(blockid = object).delete()
                    msg = "削除しました。"
                else:
                    msg = "キャンセルしました。"
                user.currentblock = 0
                user.status = "completed" #ここからだと一覧呼ばないと新規作成できない
                db.session.commit()
                lineapi.SendTextMsg(reply_token,[msg])


            elif pd[0] == "remove": #データ一覧から削除する選手を選択したとき
                object_block = int(pd[1])
                user.currentblock = int(object_block)
                user.status = "remove" #この状態から「はい」を選択すると削除となる
                db.session.commit()
                con = blockhandler.confirm_flex_data_remove(pd[1],pd[2])
                lineapi.SendFlexMsg(reply_token,con,"確認メッセージ(無視しないでね)")


            elif pd[0] == "rmconfirm": #ブロック削除確認メッセージを選択したとき
                if user.status != "remove":
                    lineapi.SendTextMsg(reply_token,["過去のボタンは押さないで～"])
                    continue
                if pd[1] == "no":
                    msg = "キャンセルしました。"
                else:
                    TimeData.query.filter_by(blockid = int(pd[1]), swimmer = pd[2]).delete()
                    msg = "削除しました。"
                user.status = "add"
                db.session.commit()
                lineapi.SendTextMsg(reply_token,[msg])


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
                con = blockhandler.BlocksFlex(blocks)
                lineapi.SendFlexMsg(reply_token,con,"現在利用可能なブロック一覧だよ～")


            #データを全取得しメールで送信する
            elif msg_text == "メール":
                user.currentblock = 0
                user.status = ""
                db.session.commit()

                block_date = blockhandler.BlockDate() #19052
                blocks = MenuBlock.query.filter_by(date = block_date).order_by(MenuBlock.blockid).all()
                text_file_content = str(block_date) + "\n"

                for b in blocks:
                    all_data_in_block = TimeData.query.filter_by(blockid = b.blockid).all()
                    rev_lists = csvmail.make_all_data_lists(b,all_data_in_block)
                    write_data = csvmail.fix_reversed_lists(rev_lists)
                    for wd_row in write_data:
                        one_row = ",".join(wd_row)
                        text_file_content += one_row + "\n\n"

                csvmail.send_mail(text_file_content)
                lineapi.SendTextMsg(reply_token,["メールで送信したと思う多分"])


            #ブロックのヘッダーステータスを編集する
            elif user.status == "define":
                new_block = MenuBlock.query.filter_by(blockid = user.currentblock).first()
                st_list = msg_text.split("\n")
                if len(st_list) == 3:
                    #replaceで通常のコンマを､(HALFWIDTH IDEOGRAPHIC COMMA)に置換している
                    #これをしないとCSVに書き出したときに区切り文字と混同してしまう
                    new_block.category = st_list[0].replace(",","､")
                    new_block.description = st_list[1].replace(",","､")
                    new_block.cycle = st_list[2].replace(",","､")

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


            #どれにも当てはまらない文字列にも一応返す
            else:
                length = len(msg_text)
                msg = "😇" * length
                lineapi.SendTextMsg(reply_token,[msg])


    return "ok"

@app.route("/create")
def create_db():
    db.create_all()
    return "ok"

@app.route("/")
def test():
    pass
    return "できたぜべいべえ"


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
