from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import SQLALCHEMY_DATABASE_URI
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'whocares'
app.config['SESSION_TYPE'] = 'filesystem'

moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)