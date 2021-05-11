import jinja2_time
from flask import Flask
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config.from_pyfile('config.py')

DB = MongoEngine(app)
app.jinja_options["extensions"].append("jinja2_time.TimeExtension")

from toolbox import views
