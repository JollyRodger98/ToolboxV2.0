from flask import Flask
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.jinja_options["extensions"].append("jinja2_time.TimeExtension")
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

DB = MongoEngine(app)

from toolbox import views
