from functools import wraps
from flask import current_app as app,render_template,session,flash,redirect,url_for,jsonify
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from db import mysql
from werkzeug.utils import secure_filename
import os
import hashlib

#using wtforms
class RegisterForm(Form):
    name = StringField('Team Name',[validators.Length(min=3,max=50,message="Name length min 3 max 50"),
                            validators.DataRequired(message="This section is required"),
                            validators.Regexp(r"^[a-zA-Z0-9_?!:)(-]*$",message="Only alnum and ?!_:)(- are allowed")])
    email = StringField('Email',[validators.length(min=9,max=50,message="Email length min 9 max 50"),
                            validators.DataRequired(message="This section is required"),
                            validators.Regexp(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",message="Not valid email!")])
    institution = StringField('Institution (optional)',[validators.Length(min=0,max=50,message="Instituion length max 50"),
                            validators.Regexp(r"^[a-zA-Z0-9]*$",message="Only alnum allowed")])
    password = PasswordField('Password',[validators.Length(min=8,max=30,message="Password length min 8 max 30"),
                            validators.DataRequired(message="This section is required"),
                            validators.Regexp(r"^[a-zA-Z0-9_?!:)(-]*$",message="Only alnum and ?!_:)(- are allowed")])

#logged in checker
def is_logged_in(f):
    @wraps(f)
    def auth_check(*args,**kwargs):
        if session.get('logged_in'):
            return f(*args,**kwargs)
        else:
            flash('Nope, Please Login First .','danger')
            return redirect(url_for('auth.login'))
    return auth_check

# logged out checker
def is_logged_out(f):
    @wraps(f)
    def logged_out(*args,**kwargs):
        if not session:
            return f(*args,**kwargs)
        else:
            flash("You Already Logged In",'danger')
            return redirect(url_for('views.home')) 
    return logged_out

def only_admin(f):
    @wraps(f)
    def admin_only(*args,**kwargs):
        if session.get('admin'):
            return f(*args,**kwargs)
        else:
            return render_template("errors/403.html")
    return admin_only


def solved(id_soal,id_team):
    cur = mysql.connection.cursor()
    hasil = cur.execute("SELECT * FROM solve JOIN challenges WHERE solve.id_soal=challenges.id AND solve.id_team=%s",(id_team,))
    mysql.connection.commit()
    cur.close()
    if hasil > 0:
        return True
    else:
        return False 

def check_flag(flag_asli,flag_submit,id_soal,id_team):
    cur = mysql.connection.cursor()
    hasil = cur.execute("SELECT * FROM solve JOIN challenges WHERE solve.id_soal=challenges.id AND solve.id_soal=%s AND solve.id_team=%s",(id_soal,id_team))
    mysql.connection.commit()
    cur.close()
    if hasil > 0:
        return {"notifsuccess" : "Your Team Already Solved This Challenge !"}
    else:
        if flag_asli == flag_submit:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO solve(id_soal,id_team) VALUES(%s,%s)",(id_soal,id_team))
            mysql.connection.commit()
            cur.execute("UPDATE users SET score=score+(SELECT poin FROM challenges WHERE id=%s), last_solve=(SELECT solve_time FROM solve WHERE id_soal=%s AND id_team=%s) WHERE id=%s",(id_soal,id_soal,id_team,id_team))     
            mysql.connection.commit()
            cur.close()
            return {"notifsuccess" : "Yeay, Correct flag"}
        else:
            return {"notiffail" : "Submitted flag is not correct !"}   

def check_id_soal(id_soal,semua=False):
    cur = mysql.connection.cursor()
    check = cur.execute("SELECT * FROM challenges WHERE id=%s",(id_soal,))
    if check > 0:
        if semua == False:
            check_data = cur.fetchone()
        if semua == True:
            check_data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return check_data 
    else:
        return None

def merge_solved_chall(check_data,id_team):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id,name,poin,deskripsi,tipe FROM challenges JOIN solve WHERE id_soal=id AND id_team=%s",(id_team,))
    hasil = cur.fetchall()
    for x in range(len(hasil)):
        for y in range(len(check_data)):
            if hasil[x]['id'] == check_data[y]['id']:
                check_data[y]['color'] = "background-color : #16CB34"
                break
    return check_data


def get_all_team():
    cur = mysql.connection.cursor()
    fetch = cur.execute("SELECT * FROM users")
    hasil = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return hasil

def get_team(id):
    cur = mysql.connection.cursor()
    fetch = cur.execute("SELECT * FROM users WHERE id=%s",(id,))
    hasil = cur.fetchone()
    mysql.connection.commit()
    cur.close()
    return hasil

def get_scoreboard(hidden):
    cur = mysql.connection.cursor()
    if hidden == True :
        fetch = cur.execute("SELECT * FROM users WHERE status='Active' ORDER BY score DESC , last_solve ASC")
        hasil = cur.fetchall()
        mysql.connection.commit()
    else:
        fetch = cur.execute("SELECT * FROM users ORDER BY score DESC , last_solve ASC")
        hasil = cur.fetchall()
        mysql.connection.commit()
    cur.close()
    return hasil


def upload_file(file, challid):
    filename = secure_filename(file.filename)

    if len(filename) <= 0:
        return False

    md5hash = hashlib.md5(os.urandom(64)).hexdigest()

    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(os.path.join(upload_folder, md5hash)):
        os.makedirs(os.path.join(upload_folder, md5hash))

    file.save(os.path.join(upload_folder, md5hash, filename))
    cur = mysql.connection.cursor()
    file_ = md5hash + '/' + filename
    cur.execute("INSERT INTO files(challid,file) VALUES(%s,%s)",(int(challid),file_))
    hasil = cur.fetchone()
    mysql.connection.commit()
    cur.close()
    return file_


def delete_file(file_id,location):
    cur = mysql.connection.cursor()
    fetch = cur.execute("DELETE FROM files WHERE id=%s",(file_id,))
    mysql.connection.commit()
    cur.close()
    upload_folder = app.config['UPLOAD_FOLDER']
    if os.path.exists(os.path.join(upload_folder,location)):  # Some kind of os.path.isfile issue on Windows...
        os.unlink(os.path.join(upload_folder,location))
        os.rmdir(os.path.join(upload_folder,location.split('/')[0]))
    return True


def get_team_solve(id):
    cur = mysql.connection.cursor()
    fetch = cur.execute("SELECT * FROM solve JOIN challenges WHERE id_team=%s AND id_soal=id ORDER BY solve_time DESC",(id,))
    hasil = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return hasil

def del_solve(id_soal,id_team):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM solve WHERE id_soal=%s AND id_team=%s",(id_soal,id_team))
    mysql.connection.commit()
    cur.execute("UPDATE users SET score=score-(SELECT poin FROM challenges WHERE id=%s), last_solve=(SELECT MAX(solve_time) FROM solve WHERE id_team=%s) WHERE id=%s",(id_soal,id_team,id_team))
    mysql.connection.commit()
    cur.close()
    return '1'

def get_solve_list():
    cur = mysql.connection.cursor()
    fetch = cur.execute("SELECT *,(SELECT name FROM users WHERE users.id = id_team) as team_name FROM solve JOIN challenges WHERE id_soal=challenges.id ORDER BY solve_time DESC")
    hasil = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return hasil

def file_per_chall(id):
    cur = mysql.connection.cursor()
    fetch = cur.execute("SELECT * FROM files WHERE challid=%s",(id,))
    hasil = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return hasil

def solves_per_soal(id):
    cur = mysql.connection.cursor()
    fetch = cur.execute("SELECT id,name,solve_time,hidden FROM solve JOIN users WHERE id_soal=%s AND id_team=id ORDER BY solve_time ASC",(id,))
    hasil = cur.fetchall()
    return hasil

def get_category():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT(tipe) FROM challenges WHERE status='Active' ORDER BY tipe DESC")
    hasil = cur.fetchall()
    return hasil

def init_errors(app):
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def general_error(error):
        return render_template('errors/500.html'), 500
