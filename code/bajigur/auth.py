from flask import Flask,render_template,flash,redirect,url_for,session,logging,request,Blueprint
from bajigur.db import mysql
from utils import *
from passlib.hash import sha256_crypt
import re

auth = Blueprint('auth',__name__)


@auth.route('/register',methods=['GET','POST'])
@is_logged_out
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        print "kok masuk"
        name = form.name.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        institution = form.institution.data

        cur = mysql.connection.cursor()
        hasil = cur.execute("SELECT * FROM users WHERE email=%s OR name=%s",(email,name))
        if hasil > 0:
            flash("Email or Team Name already exist !","danger")
            mysql.connection.commit()
            cur.close()
            return render_template("register.html",form=form)
        else:
            cur.execute("INSERT INTO users(name,email,password,institution) VALUES (%s,%s,%s,%s);",(name,email,password,institution))
        
        mysql.connection.commit()
        cur.close()
        flash('Registration Succes.Proceed to Login','success')
        return redirect(url_for('views.home'))

    return render_template('register.html',form=form)


@auth.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST' :
        email_or_team = request.form['team_or_email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        hasil = cur.execute("SELECT * FROM users WHERE email=%s OR name=%s",(email_or_team,email_or_team))
        if hasil > 0:
            data = cur.fetchone()
            mysql.connection.commit()
            cur.close()
            password_enkrip = data['password']

            if sha256_crypt.verify(password,password_enkrip):
                session['logged_in'] = True
                session['team'] = data['name']
                session['id_team'] = data['id']
                session['admin'] = data['admin']
                
                flash("Success Login.Have fun with the challenges :)","success")
                print "aaaa"
                return redirect(url_for('views.home'))
            else:
                flash("Invalid Password !","danger")
        else: 
            flash("Email or Team Doesn't Exist !","danger")

        return render_template('login.html')

    return render_template('login.html')


@auth.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash("You are now Logged-out .",'success')
    return redirect(url_for('auth.login'))


@auth.route('/profile',methods=['GET','POST'])
@is_logged_in
def profile():
    id_ = session['id_team']
    hasil = get_team(id_)
    error = dict()
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        institusi = request.form['team_institusi']
        old_pass = request.form['curr_pass']
        new_pass = request.form['new_pass']

        if len(institusi) > 0:
            if not re.match(r"^[a-zA-Z0-9]{1,50}$",institusi):
                error['inst'] = "Instituion name only accept alnum and max 50 char !"

        if len(old_pass) > 0:
            if  not sha256_crypt.verify(old_pass,hasil['password']):
                error['currpass'] = "Incorrect current password !"

        if len(new_pass) > 0:
            if not re.match(r"^[a-zA-Z0-9_?!:)(-]{8,30}$",str(new_pass)):
                error["newpass"] = "Pass length min 8 and max 30 ,also only accept alnum and ?!_:)(-"
            else:
                new_pass = sha256_crypt.encrypt(str(new_pass))

        if len(old_pass) != 0 or len(new_pass) != 0:
            if len(old_pass) == 0 and len(new_pass) > 0:
                error['currpass'] = "Current password field empty !"
            if len(old_pass) > 0 and len(new_pass) == 0:
                error['newpass'] = "New password field is empty !"
        
        if error:
            return render_template("profile.html",errors=error,data=hasil)
        else:
            if len(new_pass) >= 8 and len(old_pass) >= 8:
                cur.execute("UPDATE users SET institution=%s , password=%s WHERE id=%s",(institusi,new_pass,id_))
            else:
                cur.execute("UPDATE users SET institution=%s WHERE id=%s",(institusi,id_))

            mysql.connection.commit()
            cur.close()
            hasil['institution'] = institusi
            flash("Success Editing Your Profile","success")
            return render_template("profile.html",data=hasil,errors="")

        cur.close()

    print hasil
    return render_template('profile.html',data=hasil,errors="")
