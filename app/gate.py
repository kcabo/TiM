from app.models import db, User
from app.redis_setup import conn

class UserNotFound(Exception):
    def __init__(self, line_id):
        print(f'{line_id}による不明なアクセスを検知')


def validate_user(line_id):
    # line_idがNoneのときに注意
    menu_id = conn.get(line_id)
    if menu_id: return menu_id

    # Redis上から見つからなかったらテーブルから探査
    user = db.session.query(User.userid).filter_by(lineid=line_id).one_or_none()
    if user: return 0
    else: raise UserNotFound(line_id)
