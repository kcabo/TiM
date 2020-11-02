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
    times = db.Column(db.String(), nullable = False)                # タイム fr|0:29.47_1:01.22__0:32.43_1:11.44

    def __init__(self, menu_id: int, swimmer: str, times: str):
        self.menuid = menu_id
        self.swimmer = swimmer
        self.times = times
