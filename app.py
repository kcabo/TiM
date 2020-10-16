from flask import Flask, request

from models import db

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)

@app.route("/")
def hello():
    return "Hi!"

if __name__ == "__main__":
    app.run()
