import os

DB_URL = os.environ['DATABASE_URL']
ENVIRONMENT = os.environ['ENVIRONMENT']

class Config:
    SQLALCHEMY_DATABASE_URI = DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False # DBの変更の度にロギングするのを防ぐ
    TESTING = True
    DEBUG = False if ENVIRONMENT == 'PRODUCT' else True
