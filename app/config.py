import os

DB_URL = os.environ.get('DATABASE_URL', 'postgresql://tim:0000@localhost:5432/tim')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'DEVELOP')

class Config:
    SQLALCHEMY_DATABASE_URI = DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False # DBの変更の度にロギングするのを防ぐ
    TESTING = True
    DEBUG = False if ENVIRONMENT == 'PRODUCT' else True
