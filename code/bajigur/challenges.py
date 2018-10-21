from flask import Flask,render_template,flash,redirect,url_for,session,logging,request,Blueprint,jsonify
from utils import *
from bajigur.db import mysql

challenges = Blueprint('challenges',__name__)

@challenges.route('/challenges')
@is_logged_in
def chall_list():
    tipe_soal = get_category()
    cur = mysql.connection.cursor()
    hasil = cur.execute("SELECT * FROM challenges WHERE status='Active' ORDER BY tipe DESC , poin ASC")
    if hasil > 0:
        id_team = session['id_team']
        challs = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        challs = merge_solved_chall(challs,id_team)
        return render_template('challenges.html',jenis_soal=tipe_soal,challs=challs)
    else:
        return render_template('challenges.html')


@challenges.route('/challenge/<string:id>',methods=['GET','POST'])
@is_logged_in
def chall(id):
    if request.method == 'GET':
        data = check_id_soal(id)
        files = file_per_chall(id)
        data_files = []
        for x in files:
            data_files.append(x['file'])
        data['files'] = data_files
        return jsonify(data)
    if request.method == 'POST':
        if request.form['methodd'] == 'show_solves':
            solves_soal = solves_per_soal(id)
            return jsonify(solves_soal)
        else:
            id_team = session['id_team']
            id_soal = request.form['id_soal']
            flag_submit = request.form['flag']

            check_data = check_id_soal(id_soal)
            if check_data:
                keluar = check_flag(check_data['flag'],flag_submit,id_soal,id_team)
            else:
                keluar = {"notiffail" : "Something Goes Wrong.Invalid Challenge ID !"}
                
            return jsonify(keluar)

