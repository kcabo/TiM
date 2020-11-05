import os
from flask import Flask, request, render_template, jsonify

from app.models import db, Menu
from app.webhook import handler

LIFF_ID = os.environ['LIFF_ID']

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

@app.route('/liff', methods=['GET'])
def liff_root():
    return render_template('menu.html', LIFF_ID=LIFF_ID), 200


@app.route('/liff/menu/<int:menu_id>', methods=['GET'])
def fetch_menu(menu_id=0):
    print(menu_id)
    return render_template('menu.html', LIFF_ID=LIFF_ID), 200


@app.route('/liff/new-menu/<int:date_int>', methods=['GET'])
def new_menu(date_int=0):
    print(date_int)
    return render_template('menu.html', LIFF_ID=LIFF_ID), 200


@app.route('/liff/menu', methods=['PUT'])
def update_menu():
    menu_id = request.json['num']
    category = request.json['category']
    description = request.json['description']
    cycle = request.json['cycle']

    target_menu = Menu.query.get(menu_id)
    target_menu.category = category
    target_menu.description = description
    target_menu.cycle = cycle
    db.session.commit()
    return '200', 200


@app.route('/liff/new-menu', methods=['POST'])
def post_new_menu():
    date_int = request.json['num']
    category = request.json['category']
    description = request.json['description']
    cycle = request.json['cycle']
    new_menu = Menu(date_int, category, description, cycle)
    db.session.add(new_menu)
    db.session.commit()
    return '200', 200


@app.route('/liff/id')
def get_liff_id():
    return jsonify({'LIFFID': LIFF_ID}), 200


@app.route('/create')
def create():
    db.create_all()
    return 'Hi', 200
