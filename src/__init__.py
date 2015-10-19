from flask import Flask

from src.models import db
from src.assets_loader import assets
from src.api import api

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config.BaseConfiguration')
app.config.from_pyfile('config.py', silent=True)

api.init_app(app)
assets.init_app(app)
db.init_app(app)

import src.controllers
