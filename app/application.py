from flask import Flask, request

from app.models import db
from app.webhook import handler

app = Flask(__name__)
app.config.from_object('app.config.Config')
db.init_app(app)

@app.route('/')
def hello():
    return 'Hi'

@app.route('/callback', methods=['POST'])
def callback():
    data = request.get_json()
    # events内にWebhookイベントのリストが格納されている
    for event_json in data['events']:
        handler.handle(event_json)
    return '200 OK'
