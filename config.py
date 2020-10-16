import os

DB_URL = os.environ.get('DATABASE_URL', 'postgresql://tim:0000@localhost:5432/tim')
IS_PRODUCT = os.environ.get('IS_PRODUCT', '')

class Config:
    SQLALCHEMY_DATABASE_URI = DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False # DBの変更の度にロギングするのを防ぐ
    TESTING = True
    DEBUG = True if IS_PRODUCT else False
