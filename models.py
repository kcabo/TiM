from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Member(db.Model):
    __tablename__ = "members"
    keyid = db.Column(db.Integer, primary_key = True)
