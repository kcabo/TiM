from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy

import os
import json
import time

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
    authorized = db.Column(db.Boolean, nullable = False)
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

        if event_type != "follow": #アクセス制限管理だが、追加時はこの操作はしない
            user = UserStatus.query.filter_by(lineid = lineid).first()
            if user is None:
                lineapi.SendTextMsg(reply_token,["あなたは登録されていないユーザーです。一度ブロックして解除すれば再登録できます。"])
                print("Unknown user's access\tlineid = {}".format(lineid))
                continue
            elif user.authorized != True:
                lineapi.SendTextMsg(reply_token,["あなたの使用権限はただ今管理者によって制限されています。"])
                print("ACCESS DENIED (by {})".format(user.name))
                continue

        if event_type == "follow": #友だち追加と同時にユーザーに追加
            name = lineapi.get_line_profile(lineid)
            authorized_flag = False #ここ普段はFalseで
            reg = UserStatus(lineid = lineid, name = name, authorized = authorized_flag, status = "recruit", currentblock = 0)
            try:    #lineidにunique制約あるので二重登録しようとするとエラー発生
                db.session.add(reg)
                db.session.commit()
                lineapi.SendTextMsg(reply_token,["ようこそ{}さん、よろしくおねがいします！😇😇😇".format(name),"authorized = {}".format(authorized_flag)])
                print("REGISTER by {}. AUTHORIZED = {}".format(name,authorized_flag))
            except:
                lineapi.SendTextMsg(reply_token,["登録に失敗しました。既に登録されている可能性がございます。"])
                print("REGISTER by {}. CONFLICTED in database.".format(name))

        elif event_type == "postback": #ボタン押したときとかのポストバックイベント
            p_data = event['postback']['data']
            print("{} ――POSTBACK data:{}".format(user.name, p_data))
            pd = p_data.split("_")

            if pd[0] == "new": #一覧から新規作成を押したとき
                block_date = blockhandler.BlockDate() #190520
                blocks = MenuBlock.query.filter_by(date = block_date).order_by(MenuBlock.blockid).all() #今日使ってるブロックを全部持ってくる
                if len(blocks) == 0:
                    new_block_id = block_date * 100 + 1
                else:
                    new_block_id = blocks[-1].blockid + 1 #並び替えて一番最後になったブロックのIDが最大

                try:
                    mb = MenuBlock(blockid = new_block_id, date = block_date, category = "", description = "", cycle = "")
                    db.session.add(mb)
                    db.session.commit() #もしすでに登録されているブロックIDを追加しようとしたらエラーになる
                except:
                    lineapi.SendTextMsg(reply_token,["上手く作成できませんでした😥😥\nもう一度一覧から新規作成を試してください。"])
                else:
                    user.currentblock = new_block_id
                    user.status = "define" #この状態で受け取った文字列はブロック名編集となる
                    db.session.commit()
                    new_block_msg = ["メニューの情報を３行で教えて！😮\n例：\nSwim\n50*8*1 HighAverage\n1:00"]
                    lineapi.SendTextMsg(reply_token,new_block_msg)


            elif pd[0] == "header":
                target_blc = int(pd[1])
                if_exist = MenuBlock.query.filter_by(blockid = target_blc).first()
                if if_exist == None:
                    lineapi.SendTextMsg(reply_token,["対象のブロックが見つからないよ！😭😭"])
                    continue
                user.currentblock = target_blc
                user.status = "define" #この状態で受け取った文字列はブロック名編集となる
                db.session.commit()
                lineapi.SendTextMsg(reply_token,["メニューの情報を３行で教えて！😮\n例：\nSwim\n50*8*1 HighAverage\n1:00"])


            elif pd[0] == "switch": #一覧から切り替えを押したとき
                target_blc = int(pd[1])
                if_exist = MenuBlock.query.filter_by(blockid = target_blc).first()
                if if_exist == None:
                    lineapi.SendTextMsg(reply_token,["対象のブロックが見つからないよ！😭😭"])
                    continue
                user.currentblock = target_blc
                user.status = "add" #この状態で受け取った文字列は通常のデータ登録となる
                db.session.commit()

                all_data = TimeData.query.filter_by(blockid = target_blc).all()
                switch_block = MenuBlock.query.filter_by(blockid = target_blc).first()
                list = blockhandler.get_time_data_all_list(all_data)
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
                lineapi.versatile_send_msgs(reply_token,msgs)


            elif pd[0] == "delete": #一覧から削除を押したとき
                target_blc = pd[1]
                user.currentblock = int(target_blc)
                user.status = "delete" #この状態から「はい」を選択すると削除となる
                db.session.commit()
                confirm_msg = "本当にBlockID:{}を削除しますか？\n⚠⚠この操作は元に戻せません！！⚠⚠".format(target_blc)
                con = blockhandler.ConfirmTemplate(confirm_msg)
                lineapi.SendTemplatexMsg(reply_token,con,"確認メッセージ(無視しないでね)")


            elif pd[0] == "confirm": #ブロック削除確認メッセージを選択したとき
                answer = pd[1]
                if user.status != "delete":
                    lineapi.SendTextMsg(reply_token,["過去のボタンは押さないで～🗿"])
                    continue
                if answer == "yes":
                    target_blc = user.currentblock
                    MenuBlock.query.filter_by(blockid = target_blc).delete()
                    TimeData.query.filter_by(blockid = target_blc).delete()
                    msg = "削除したよ！💀💀"
                else:
                    msg = "キャンセルしたよ💨"
                user.currentblock = 0
                user.status = "" #ここからだと一覧呼ばないと新規作成できない
                db.session.commit()
                lineapi.SendTextMsg(reply_token,[msg])


            elif pd[0] == "remove": #データ一覧から削除する選手を選択したとき
                object_block = int(pd[1])
                user.currentblock = int(object_block)
                user.status = "remove" #この状態から「はい」を選択すると削除となる
                db.session.commit()
                con = blockhandler.confirm_flex_data_remove(pd[1],pd[2])
                lineapi.SendFlexMsg(reply_token,con,"確認メッセージ(無視しないでね)")


            elif pd[0] == "rmconfirm": #データ一覧から削除確認メッセージを選択したとき
                if user.status != "remove":
                    lineapi.SendTextMsg(reply_token,["過去のボタンは押さないで～🗿"])
                    continue
                if pd[1] == "no":
                    msg = "キャンセルしたよ💨"
                else:
                    TimeData.query.filter_by(blockid = int(pd[1]), swimmer = pd[2]).delete()
                    msg = "削除したよ！💀💀"
                user.status = "add" #一選手のデータを削除しただけなのでそのまま編集できる
                db.session.commit()
                lineapi.SendTextMsg(reply_token,[msg])


        elif event_type == "message": #なにかがユーザーに送られてきたときどうするか
            msg_type = event['message']['type']
            if msg_type != "text": #テキスト以外は適当なスタンプを返す
                msg_reply_sticker = {
                "type": "sticker",
                "packageId": "11539",
                "stickerId": "52114140"
                }
                lineapi.versatile_send_msgs(reply_token,[msg_reply_sticker])
                msg_id =  event['message']['id']
                print("{} ――NOT TEXT type:{} msgid:{}".format(user.name, msg_type, msg_id))
                # msg_type_list = ["image", "video", "audio", "file"]
                if msg_type == "image":
                    res = lineapi.get_content_binary(msg_id)
                    csvmail.send_notify_image_mail(res, user.name)
                    print("{} ――IMAGE SENT".format(user.name))
                continue

            msg_text = event['message']['text']

            #ブロック一覧を表示する ブロックIDとステータスは一覧をみるとリセットされる
            if msg_text == "一覧":
                try:
                    block_date = blockhandler.BlockDate() #190520
                    blocks = MenuBlock.query.filter_by(date = block_date).order_by(MenuBlock.blockid).limit(9).all() #ちなみにここメニュー9個分までしかできない 一日9個以上ってことはないでしょ多分
                    con = blockhandler.BlocksFlex(blocks)
                    lineapi.SendFlexMsg(reply_token, con, "メニュー一覧だよ！どれかを選択してデータを登録してね✨")
                    print(blocks)
                except:
                    print("{} ――ERROR RAISED in 一覧".format(user.name))
                user.currentblock = 0
                user.status = ""
                db.session.commit()

            elif msg_text == "確認" or msg_text == "修正":
                target_blc = user.currentblock
                if_exist = MenuBlock.query.filter_by(blockid = target_blc).first()
                if target_blc == 0 or user.status != "add":
                    lineapi.SendTextMsg(reply_token,["ブロックが選択されてないよ！😭😭一覧からどれか選択してね"])
                    continue
                elif if_exist == None:
                    lineapi.SendTextMsg(reply_token,["対象のブロックが見つからないよ！😭😭"])
                    user.status = ""
                    db.session.commit()
                    continue

                all_data = TimeData.query.filter_by(blockid = target_blc).all()
                switch_block = MenuBlock.query.filter_by(blockid = target_blc).first()
                list = blockhandler.get_time_data_all_list(all_data)
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
                lineapi.versatile_send_msgs(reply_token,msgs)

            #データを全取得しメールで送信する
            elif msg_text == "メール":
                start_t = time.time()
                user.currentblock = 0
                user.status = ""
                db.session.commit()
                block_date = blockhandler.BlockDate() #190520
                blocks = MenuBlock.query.filter_by(date = block_date).order_by(MenuBlock.blockid).all()
                text_file_content = ""

                for b in blocks:
                    all_data_in_block = TimeData.query.filter_by(blockid = b.blockid).all()
                    rev_lists = csvmail.make_all_data_lists(b,all_data_in_block)
                    write_data = csvmail.fix_reversed_lists(rev_lists)
                    for wd_row in write_data:
                        one_row = ",".join(wd_row)
                        text_file_content += one_row + "\n"
                    text_file_content += ".\n"

                if text_file_content == "":
                    lineapi.SendTextMsg(reply_token,["メールで送るデータがないよ👻"])
                else:
                    elapsed_time = time.time() - start_t
                    csvmail.send_mail(text_file_content, str(block_date), elapsed_time)
                    msg_otsukaresama = [{
                    "type": "sticker",
                    "packageId": "11537",
                    "stickerId": "52002734"
                    },
                    {
                      'type' : 'text',
                      'text' : "メールで送ったよ！ありがとう！おつかれさま！😆😆"
                    }]
                    lineapi.versatile_send_msgs(reply_token,msg_otsukaresama)
                    print("{} ――MAIL date:{}".format(user.name, block_date))

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
                    lineapi.SendTextMsg(reply_token,["メニューの情報を記録したよ📊このまま選手のタイムを入力できるよ！📋"])
                else:
                    lineapi.SendTextMsg(reply_token,["とりあえず適当でいいから３行でメニューの情報を教えて欲しいです。。。"])


            #timedataテーブルに新しい記録を追加する
            elif msg_text.find("\n") > 0: #改行が含まれるときは登録と判断
                if user.status != "add":
                    lineapi.SendTextMsg(reply_token,["もう一度一覧からブロックを選択してね🗂🗂"])
                    continue
                rows = msg_text.split("\n")
                swimmer = rows[0]
                currentblock = user.currentblock
                existing_rows = TimeData.query.filter_by(blockid = currentblock, swimmer = swimmer).first()

                #既にその選手のデータがある場合、破壊的更新を試してみる
                if existing_rows != None:
                    for i, row in enumerate(rows):
                        if i != 0 and row != "": #2行目以降で何かしら書いてある行
                            if len(row) > 12: #変に長い文字列を見つけた瞬間に処理をやめる
                                lineapi.SendTextMsg(reply_token,["一行あたりの文字数が12を超えたのでデータ登録でないと判断しました。処理を中断します。"])
                                break
                            r = valueconv.RowSeparator(row)
                            existing_row = TimeData.query.filter_by(blockid = currentblock, swimmer = swimmer, row = i).first()
                            if existing_row is not None and existing_row.data == "" and existing_row.style == None: #同じ行が存在しておりかつデータが無いとき破壊的更新を実行可能とする
                                existing_row.data = r.data
                                existing_row.style = r.style
                                db.session.commit()
                            else:
                                lineapi.SendTextMsg(reply_token,["Destructive Update <Failed>", "target:= {}".format(swimmer)])
                                break

                    else: #このelseはrowsで回すfor文が正常に(breakせずに)終了したときのみ実行
                        try:
                            # db.session.commit()
                            updated_rows = TimeData.query.filter_by(blockid = currentblock, swimmer = swimmer).all()
                            show_data_as_reply = [updated_rows[0].swimmer]
                            for j in len(updated_rows):
                                if updated_rows[j].style is None:
                                    show_data_as_reply.append(updated_rows[j].style + "  " + updated_rows[j].data)
                                else:
                                    show_data_as_reply.append(updated_rows[j].data)
                            msg = "\n".join(show_data_as_reply)
                            lineapi.SendTextMsg(reply_token,["Destructive Update <Commit>", msg])
                        except:
                            lineapi.SendTextMsg(reply_token,["上手く登録できませんでした。。。😔もう一度試してみてね"])

                    # lineapi.SendTextMsg(reply_token,["その選手のデータはもう登録されてるみたい！🔗🔗"])
                    # continue

                else:
                    show_data_as_reply = [swimmer]
                    for i, row in enumerate(rows):
                        if i != 0: #０個目は名前が書いてあるから飛ばす
                            if len(row) > 12: #変に長い文字列を見つけた瞬間に処理をやめる
                                lineapi.SendTextMsg(reply_token,["一行あたりの文字数が12を超えたのでデータ登録でないと判断しました。処理を中断します。"])
                                break
                            td = TimeData()
                            td.blockid = currentblock
                            td.row = i
                            td.swimmer = swimmer
                            r = valueconv.RowSeparator(row)
                            td.style = r.style #styleなしならNoneになる
                            td.data = r.data    #dataなしなら""になる
                            db.session.add(td)
                            show_data_as_reply.append(r.merged_data())

                    else: #このelseはrowsで回すfor文が正常に(breakせずに)終了したときのみ実行
                        try:
                            db.session.commit()
                            msg = "\n".join(show_data_as_reply)
                            lineapi.SendTextMsg(reply_token,[msg,"✨✨登録成功！✨✨"])
                        except:
                            lineapi.SendTextMsg(reply_token,["上手く登録できませんでした。。。😔もう一度試してみてね"])


            #どれにも当てはまらない文字列にも一応返す
            else:
                length = len(msg_text)
                if length > 500:
                    msg = "やかましいわ"
                elif length > 200:
                    msg = "怒りますよ…"
                else:
                    msg = "🗿" * length
                lineapi.SendTextMsg(reply_token,[msg])

            print("■{} ――TEXT: {}".format(user.name, msg_text.replace("\n", "")))
    return "ok"

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
    query = TimeData.query.all
    db.session.delete(query)
    db.session.commit()
    return "deleted"

@app.route("/")
def test():
    pass
    return "This is a test route."


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
