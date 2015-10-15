from flask import Flask
from src.models import db
from flask_migrate import Migrate

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py', silent=True)

db.init_app(app)
migrate = Migrate(app, db)
