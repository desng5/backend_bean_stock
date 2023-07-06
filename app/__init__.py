from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login'
login.login_message_category = 'warning'

from .api import api
app.register_blueprint(api)

from app import routes, models