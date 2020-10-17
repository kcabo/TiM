from flask import Flask, request

from app.models import db
from app import hoge

app = Flask(__name__)
app.config.from_object('app.config.Config')
db.init_app(app)

@app.route('/')
def hello():
    return 'Hi'

@app.route('/callback', methods=['POST'])
def callback():
    data = request.get_json()
    for event_json in data['events']:
        pass
    return '200 OK'

@app.route('/create')
def create():
    hoge.init_db()
    return 'Hi'

@app.route('/add')
def add():
    hoge.add_record()
    return 'Hi'
