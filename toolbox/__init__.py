from flask import Flask
from flask_mongoengine import MongoEngine
from flask.logging import logging

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.jinja_env.add_extension("jinja2_time.TimeExtension")
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

DB = MongoEngine(app)

import toolbox.endpoints
from toolbox.models import LiveDataFilter

logging.getLogger("werkzeug").addFilter(LiveDataFilter())
