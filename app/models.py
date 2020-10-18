from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    userid = db.Column(db.Integer, primary_key = True)              # 主キー
    name = db.Column(db.String(), nullable = False)                 # 名前 名字のみ
    lineid = db.Column(db.String(), unique = True, nullable = False)# LINEユーザーID "U4af4980629..."
    gen = db.Column(db.Integer, nullable = False)                   # 期
    email = db.Column(db.String(), nullable = False)                # メアド
    role = db.Column(db.String(), nullable = False)                 # 権限（EDITOR, ADMIN）

    # def __init__(self, line_id):
    #     self.lineid = line_id
    #     self.name = '不明なユーザー'
    #     self.gen = 0
    #     self.email = 'you@example.com'
    #     self.role = 'FRIEND'

class Menu(db.Model):
    __tablename__ = "menus"
    menuid = db.Column(db.Integer, primary_key=True)                # 主キー
    date = db.Column(db.Integer, nullable = False)                  # 日付 yyMMDD 201017
    category = db.Column(db.String(), nullable = False)             # カテゴリ Swim
    description = db.Column(db.String(), nullable = False)          # 説明 50*4*1 Des to Hard
    cycle = db.Column(db.String(), nullable = False)                # サイクル 1:30

class Record(db.Model):
    __tablename__ = "records"
    recordid = db.Column(db.Integer, primary_key=True)              # 主キー
    menuid = db.Column(db.Integer, nullable = False)                # メニューIDの外部キー 制約なし
    swimmer = db.Column(db.String(), nullable = False)              # 選手名
    times = db.Column(db.String(), nullable = False)                # タイム（カンマ繋がり）fr@0:29.47,1:01.22,,0:32.43,1:11.44
