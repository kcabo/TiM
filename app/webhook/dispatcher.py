import datetime

from app.models import db, Menu
from app.webhook import flex
from app.gate import set_current_menu_id


def view_menus(event, target_date: datetime.date):
    int_date = int(target_date.strftime('%y%m%d')) # unsafe
    menus = Menu.query.filter_by(date=int_date).order_by(Menu.menuid).all()
    flex_msgs = flex.build_menus(target_date, menus)
    alt_text = 'メニュー一覧'
    event.send_flex(alt_text, flex_msgs)
    set_current_menu_id(event.line_id, 0)
