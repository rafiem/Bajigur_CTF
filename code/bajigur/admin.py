from flask import current_app as app,Flask,render_template,flash,redirect,url_for,session,logging,request,Blueprint
from bajigur.db import mysql
from utils import *
import os
import re
from passlib.hash import sha256_crypt

admin = Blueprint('admin',__name__)

@admin.route('/admin')
@is_logged_in
@only_admin
def admin_():
    flash("WELCOME ADMIN !!!","success")
    return render_template('admin/admin.html')


@admin.route('/admin/challenges')
@is_logged_in
@only_admin
def challs():
    cur = mysql.connection.cursor()
    fetch = cur.execute("SELECT id,name,poin,tipe,status FROM challenges")
    hasil = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return render_template('admin/challenges.html',hasil=hasil)

@admin.route('/admin/challenge/edit',methods=['POST','GET'])
@is_logged_in
@only_admin
def edit_challs():
    if request.method == 'POST':
        id_ = request.form['id']
        hasil = check_id_soal(id_,semua=True)
        return hasil
    else:
        return redirect(url_for('admin.challs'))
    

@admin.route('/admin/challenge/create',methods=['POST','GET'])
@is_logged_in
@only_admin
def create_chall():
    if request.method == 'POST':
        nama = request.form['nama']
        tipe = request.form['tipe']
        deskripsi = request.form['deskripsi']
        poin = request.form['poin']
        flag = request.form['flag']

        if not poin.isdigit():  
            flash("Chall Poin must be integer !","danger")
            return redirect(url_for('admin.challs'))

        cur = mysql.connection.cursor()
        fetch = cur.execute("INSERT INTO challenges(name,tipe,deskripsi,poin,flag) VALUES(%s,%s,%s,%s,%s)",(nama,tipe,deskripsi,poin,flag))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('admin.challs'))

    return redirect(url_for('admin.challs'))


@admin.route('/admin/challenge/edit/<string:id>',methods=['GET','POST'])
@is_logged_in
@only_admin
def edit_chall(id):
    if request.method == 'GET':
        id_soal = id
        data_soal = check_id_soal(id_soal)
        return jsonify(data_soal)
    if request.method == 'POST':
        nama = request.form['nama']
        if len(nama) > 50:
            flash("Chall name too long,max 50 char !","danger")
            return redirect(url_for('admin.challs'))
        tipe = request.form['tipe']
        deskripsi = request.form['deskripsi']
        poin = request.form['poin']
        flag = request.form['flag']

        cur = mysql.connection.cursor()
        fetch = cur.execute("UPDATE challenges SET name=%s,tipe=%s,deskripsi=%s,poin=%s,flag=%s WHERE id=%s",(nama,tipe,deskripsi,poin,flag,id))
        mysql.connection.commit()
        cur.close()
        if fetch > 0:
            flash("Success Editing Chall !","success")
        else:
            flash("Fail to Edit Chall,Something went wrong !","danger")
        return redirect(url_for('admin.challs'))       


@admin.route('/admin/challenge/delete/<string:id>')
@is_logged_in
@only_admin
def delete_chall(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM solve WHERE id_soal=%s",(id,))
    mysql.connection.commit()
    
    hasil = cur.fetchall()
    print hasil
    for x in hasil:
        del_solve(x['id_soal'],x['id_team'])
    
    files = file_per_chall(id)
    print files
    for y in files:
        delete_file(y['id'],y['file'])

    cur.execute("DELETE FROM challenges WHERE id=%s",(id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('admin.challs'))


@admin.route('/admin/files/<string:challid>',methods=['GET','POST'])
@is_logged_in
@only_admin
def admin_files(challid):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        fetch = cur.execute("SELECT * FROM files WHERE challid=%s",(challid,))
        files = cur.fetchall()
        json_data = {'files': []}
        for x in files:
            json_data['files'].append({'id': x['id'], 'file': x['file'], 'challid': x['challid']})
        return jsonify(json_data)
    elif request.method == 'POST':
        if request.form['method'] == 'upload':
            files = request.files.getlist('files[]')

            for f in files:
                upload_file(file=f, challid=challid)
            
            return '1'
        elif request.form['method'] == 'delete':
            location = request.form['location']
            id_ = request.form['id']
            delete_file(id_,location)
            return '1'


@admin.route('/admin/teams')
@is_logged_in
@only_admin
def admin_showteams():
    data = get_all_team()
    return render_template('admin/teams.html',data=data)


@admin.route('/admin/team/delete/<string:id>')
@is_logged_in
@only_admin
def delete_team(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM solve WHERE id_team=%s",(id,))
    mysql.connection.commit()
    cur.execute("DELETE FROM users WHERE id=%s",(id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('admin.admin_showteams'))


@admin.route('/admin/team/<string:id>',methods=['GET','POST'])
@is_logged_in
@only_admin
def admin_team(id):
    team = get_team(id)
    error_reset = ''
    if request.method == 'GET':
        return render_template('admin/team.html',data=team)
    elif request.method == 'POST':
        reset_pass = request.form["reset_pass"]
        if len(reset_pass) > 0:
            if not re.match(r"^[a-zA-Z0-9_?!:)(-]{8,30}$",str(reset_pass)):
                error_reset = "Pass length min 8 and max 30 ,also only accept alnum and ?!_:)(-"
            else:
                flash("Password Reset Success !","success")
                new_pass = sha256_crypt.encrypt(str(reset_pass))
                cur = mysql.connection.cursor()
                cur.execute("UPDATE users SET password=%s WHERE id=%s",(new_pass,id))
                mysql.connection.commit()
                cur.close()
        else:
            error_reset = "New password field is empty !"
        print error_reset
        return render_template('admin/team.html',data=team,error=error_reset)


@admin.route('/admin/solve/delete/<string:id_team>/<string:id_soal>')
@is_logged_in
@only_admin
def delete_solve(id_team,id_soal):
    del_solve(id_soal,id_team)
    print id_team,id_soal
    return redirect(url_for('admin.solves'))

@admin.route('/admin/solves')
@is_logged_in
@only_admin
def solves():
    solves = get_solve_list()
    return render_template('admin/solves.html',solves=solves)


@admin.route('/admin/scoreboard')
@is_logged_in
@only_admin
def scoreboard():
    list_standing = get_scoreboard(False)
    return render_template('admin/scoreboard.html',scores=list_standing)


@admin.route('/admin/sethidden',methods=['POST'])
@is_logged_in
@only_admin
def sethidden():
    if request.method == 'POST':
        status = request.form["status"]
        id_ = request.form["id"]
        context = request.form["context"]
        if status == "Hidden":
            stats = "Active"
        elif status == "Active":
            stats = "Hidden"

        cur = mysql.connection.cursor()
        if context == "soal":
            cur.execute("UPDATE challenges SET status=%s WHERE id=%s",(stats,id_))
        elif context == "team":
            cur.execute("UPDATE users SET status=%s WHERE id=%s",(stats,id_))
        mysql.connection.commit()
        cur.close()
        return stats


