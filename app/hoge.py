from app.models import db, Record

def init_db():
    db.create_all()

def add_record():
    new = Record()
    new.menuid = 1
    new.swimmer = 'reo'
    new.times = '34'
    db.session.add(new)
    db.session.commit()
