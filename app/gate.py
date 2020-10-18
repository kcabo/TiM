from app.models import db, User
from app.redis_setup import conn

class UserState:
    def __init__(self, line_id, menu_id=0, authorized=True):
        self.line_id = line_id
        self.menu_id = menu_id
        self.authorized = authorized

    def set_current_menu_id(new_menu_id):
        conn.set(self.line_id, new_menu_id)


def validate_user(line_id):
    # line_idがNoneのときに注意
    menu_id = conn.get(line_id)
    if menu_id: return UserState(line_id, menu_id)

    # Redis上から見つからなかったらテーブルから探査
    user = db.session.query(User.role).filter_by(lineid=line_id).one_or_none()
    if user.role in ['EDITOR', 'ADMIN']:
        return UserState(line_id)
    else:
        return UserState(line_id, authorized=False)
