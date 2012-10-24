"""
Initialize Flask app

"""

from flask import Flask
from application.aqua import seafood

app = Flask('application')
app.register_blueprint(seafood)
app.config.from_object('application.settings')

import urls
