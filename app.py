from flask import Flask
from models import db
import os


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "moviewebapp.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.route("/")
def home():
    return "MoviWeb läuft ✅"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5002)
