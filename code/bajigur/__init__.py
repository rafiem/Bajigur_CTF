from flask import Flask
from utils import *
import os

def run_app(config='bajigur.config.Config'):
    app = Flask(__name__)
    with app.app_context():
        app.config.from_object(config)

        from bajigur.db import mysql 
        mysql.init_app(app)
        init_errors(app)

        from bajigur.auth import auth
        from bajigur.views import views
        from bajigur.challenges import challenges
        from bajigur.admin import admin

        app.register_blueprint(views)
        app.register_blueprint(challenges)
        app.register_blueprint(auth)
        app.register_blueprint(admin)

        return app







