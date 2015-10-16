from flask import Flask
from flask_migrate import Migrate
from src.models import db
from src.assets_loader import assets

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py', silent=True)

assets.init_app(app)
db.init_app(app)
migrate = Migrate(app, db)


import src.controllers
