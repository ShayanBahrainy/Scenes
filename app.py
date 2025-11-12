from flask import Flask
from models import db
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SCENERY_DB_URI")

db.init_app(app)
