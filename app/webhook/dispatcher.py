import datetime

from app.models import db, Menu
from app.webhook import flex
from app.gate import set_current_menu_id


def view_menus(target_date: datetime.date):
    int_date = int(target_date.strftime('%y%m%d')) # unsafe
    menus = Menu.query.filter_by(date=int_date).order_by(menuid).all()
