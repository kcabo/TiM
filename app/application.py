import os
from flask import Flask, request, render_template, jsonify, make_response

from app.models import db, Menu
from app.webhook import handler

LIFF_ID = os.environ['LIFF_ID']

class MyFlask(Flask):
    def get_send_file_max_age(self, name):
        if name.lower().endswith('.css'):
            return 0
        return Flask.get_send_file_max_age(self, name)

app = MyFlask(__name__, template_folder='liff/templates', static_folder='liff/static')

# app = Flask(__name__, template_folder='liff/templates', static_folder='liff/static')
app.config.from_object('app.config.Config')
db.init_app(app)

@app.route('/')
def hello():
    return 'Hi'


@app.route('/webhook', methods=['POST'])
def webhook_handler():
    data = request.get_json()
    # events内にWebhookイベントのリストが格納されている
    for event_json in data['events']:
        handler.handle(event_json)
    return '200 OK'


@app.route('/liff', methods=['GET'])
def liff_origin():
    return render_template('liff.html', LIFF_ID=LIFF_ID)


@app.route('/liff/menu/<int:num>', methods=['GET'])
@app.route('/liff/new-menu/<int:num>', methods=['GET'])
def menu_modifier(num):
    response = make_response(render_template('menu.html', LIFF_ID=LIFF_ID))
    # response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    # response.headers["Pragma"] = "no-cache"
    # response.headers["Expires"] = "0"
    # response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.route('/liff/menu/<int:menu_id>', methods=['PUT'])
def update_menu(menu_id):
    category = request.json['category']
    description = request.json['description']
    cycle = request.json['cycle']

    target_menu = Menu.query.get(menu_id)

    if target_menu is None:
        return 'Failed'
    target_menu.category = category
    target_menu.description = description
    target_menu.cycle = cycle
    db.session.commit()
    return str(menu_id)


@app.route('/liff/new-menu/<int:date_int>', methods=['POST'])
def post_new_menu(date_int):
    category = request.json['category']
    description = request.json['description']
    cycle = request.json['cycle']
    new_menu = Menu(date_int, category, description, cycle)
    db.session.add(new_menu)
    db.session.commit()
    menu_id = new_menu.menuid
    return str(menu_id)


@app.route('/liff/menu/<int:menu_id>/ajax', methods=['GET'])
def fetch_menu_status(menu_id):
    menu = Menu.query.get(menu_id)

    if menu is None:
        return jsonify({'message': 'メニューが見つかりませんでした'})

    response = {
        'message': 'Success',
        'date': menu.date,
        'category': menu.category,
        'description': menu.description,
        'cycle': menu.cycle
    }
    return jsonify(response)



@app.route('/liff/id')
def get_liff_id():
    return jsonify({'LIFFID': LIFF_ID})


@app.route('/create')
def create():
    db.create_all()
    return 'Hi'
