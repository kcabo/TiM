import os
from flask import Flask, request, render_template, jsonify

from app.models import db
from app.webhook import handler

app = Flask(__name__, template_folder='liff/templates', static_folder='liff/static')
app.config.from_object('app.config.Config')
db.init_app(app)

@app.route('/')
def hello():
    return 'Hi', 200


@app.route('/webhook', methods=['POST'])
def webhook_handler():
    data = request.get_json()
    # events内にWebhookイベントのリストが格納されている
    for event_json in data['events']:
        handler.handle(event_json)
    return '200 OK', 200


@app.route('/liff/menu')
def menu_page():
    return render_template('menu.html'), 200


@app.route('/liff/id')
def get_liff_id():
    LIFF_ID = os.environ['LIFF_ID']
    return jsonify({'LIFFID': LIFF_ID}), 200


@app.route('/create')
def create():
    db.create_all()
    return 'Hi', 200
