from flask import current_app as app,Flask,render_template,flash,redirect,url_for,session,logging,request,Blueprint,send_file
from bajigur.utils import *
from bajigur.db import mysql
from flask.helpers import safe_join

views = Blueprint('views',__name__)

@views.route('/')
def welcome():
    return render_template('welcome.html')

@views.route('/home')
def home():
    return render_template('home.html')

@views.route('/teams')
def teams():
    team_list = get_all_team()
    return render_template('teams.html',teams=team_list)

@views.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@views.route('/scoreboard')
def scoreboard():
    scoreboard = get_scoreboard(True)
    return render_template('scoreboard.html',scores=scoreboard)


@views.route('/files', defaults={'path': ''})
@views.route('/files/<path:path>')
@is_logged_in
def file_handler(path):
    cur = mysql.connection.cursor()
    fetch = cur.execute("SELECT * from files where file=%s",(path,))
    if fetch > 0:
        upload_folder = app.config['UPLOAD_FOLDER']
        return send_file(safe_join(upload_folder, path))
    else:
        return 'FILE NOT FOUND!'


@views.route('/team/<string:id>')
def team(id):
    data = get_team_solve(id)
    team = get_team(id)
    return render_template('team.html',data=data,team=team)


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


