import datetime

from app.models import db, Menu
from app.webhook import flex


def view_menus(event, target_date: datetime.date):
    int_date = int(target_date.strftime('%y%m%d')) # unsafe
    menus = Menu.query.filter_by(date=int_date).order_by(Menu.menuid).all()
    flex_msgs = flex.build_menus(target_date, menus)
    alt_text = 'メニュー一覧'
    event.send_flex(alt_text, flex_msgs)
    event.aim_menu_id(0)

# import json
# fj = json.dumps(flex_msgs[0])
# with open('safe/trash/b.py', mode='w', encoding='UTF8') as f:
#     print(fj, file=f)
