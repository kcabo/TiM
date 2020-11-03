import os

DB_URL = os.environ['DATABASE_URL']

class Config:
    SQLALCHEMY_DATABASE_URI = DB_URL
    
    # DBの変更の度にロギングするのを防ぐ
    SQLALCHEMY_TRACK_MODIFICATIONS = False
