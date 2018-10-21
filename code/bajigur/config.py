import os
from flask import current_app as app
key = os.urandom(64)

class Config(object):
    SECRET_KEY = key
    MYSQL_HOST = 'SQL_SERVER_ADDRESS'
    MYSQL_USER = 'SQL_USERNAME'
    MYSQL_DB   = 'SQL_DB'
    MYSQL_PASSWORD = 'SQL_PASSWORD'
    MYSQL_CURSORCLASS = 'DictCursor'
    MYSQL_PORT = 3308
    UPLOAD_FOLDER = os.path.join(os.path.normpath(app.root_path), 'uploads')
    SEND_FILE_MAX_AGE_DEFAULT = 0
