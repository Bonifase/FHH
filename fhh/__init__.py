import os
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from config import app_config

app = Flask(__name__)
mail = Mail(app)
db = SQLAlchemy(app)

from fhh import routes  # noqa

app.config['JWT_SECRET_KEY'] = 'supersecretishere'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

app.config.from_object(app_config["development"])
