import sqlite3
import os
import PIL 
from pathlib import Path
from flask import Flask,request,render_template,session,redirect
from werkzeug.utils import secure_filename
from flask_sessions import Session
app = Flask(__name__)
app.config["UPLOAD_FOLDER"]=r"D:\my project cs50\templates\images"
conn=sqlite3.connect('abcd.db',check_same_thread=False)
cur = conn.cursor()
conn.commit()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = '123456'
#from werkzeug.security import check_password_hash, generate_password_hash
@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        username=request.form.get('username')
        password=request.form.get('password')
        cur.execute('select * from users where user_id=? and password=?',(username,password))
        try:
            f=list(cur.fetchone())
            session["user_id"]=f[0]
            return redirect('/home')
        except:
            return render_template('error.html',e='incoorect password or username')
    return render_template('login.html')
@app.route('/search',methods=['GET','POST'])
def search():
    if request.method == 'GET':
        return render_template('search.html',marks='hello')
    else:
        regd=request.form.get('regd_search')
        cur.execute('Select * from marks where regd=?',(regd,))
        try:
            d=list(cur.fetchall())
            return render_template('search.html',marks=d)
        except:
            return render_template('error.html',e="Record not found")
    
@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'POST':
        username=request.form.get('user_name')
        pass1=request.form.get('pass')
        cnf_pass=request.form.get('cnf_pass')
        if pass1!=cnf_pass:
            return 'not same'
        cur.execute('select user_id from users  where user_id=?',(username,))
        try:
            cur.execute('INSERT into users(user_id,password) VALUES(?,?)',(username,pass1))
            conn.commit()
        except:
            return 'already  taken'
        return render_template('register.html')
    else:
        return render_template('register.html')
@app.route('/upload',methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        regd=request.form.get('regd')
        sem=request.form.get('semster')
        sub1=request.form.get('submarks_1')
        sub2=request.form.get('submarks_2')
        sub3=request.form.get('submarks_3')
        sub1=int(sub1)
        sub2=int(sub2)
        sub3=int(sub3)
        percent=(sub1+sub2+sub3)/3
        cur.execute('select * from marks where regd=? and sem=?',(regd,sem))
        c=cur.fetchone()
        try:
            c=list(c)
            return render_template('error.html',e="Record already Exists")
        except:
            cur.execute('INSERT INTO MARKS VALUES(?,?,?,?,?,?)',(regd,sem,sub1,sub2,sub3,percent))
            conn.commit()
            return redirect('/home')
    else:
      return render_template('upload.html')
@app.route('/logout',methods=['GET','POST'])
def logout():
    session.clear()
    return redirect('/')
@app.route('/update',methods=['GET','POST'])
def update():
    if request.method == 'POST':
        regd = request.form.get('regd_update')
        sub = request.form.get('sub_update')
        updated=request.form.get('updated_value')
        updated=int(updated)
        sem=request.form.get('sem')
        if sub=='sub1':
            cur.execute('UPDATE MARKS set sub1=? where regd=? AND sem=?',(updated,regd,sem))
        elif sub=='sub2':
            cur.execute('UPDATE MARKS set sub2=? where regd=? AND sem=?',(updated,regd,sem))
        else:
            cur.execute('UPDATE MARKS set sub3=? where regd=? AND sem=?',(updated,regd,sem))
        conn.commit()
        cur.execute('Select sub1,sub2,sub3 from marks where regd=? and sem=?',(regd,sem))
        cur.execute('select sub1,sub2,sub3 from marks where regd=?',(regd,))
        row = list(cur.fetchone())
        for i in range(len(row)):
            row[i]=int(row[i])
        sum=row[0]+row[1]+row[2]
        percentage=sum/3
        cur.execute('UPDATE MARKS set percentage=? where regd=? AND sem=?',(percentage,regd,sem))
        conn.commit()
        return redirect('/home')
    else:
        return render_template('update.html')
@app.route('/delete',methods=['GET','POST'])
def delete():
    if request.method == 'POST':
        regd=request.form.get('regd_deleted')
        sem=request.form.get('semster_deleted')
        sem=int(sem)
        try:
            cur.execute('Select * from marks where regd=? and sem=?',(regd,sem))
            l=cur.fetchone()
            c=l[0]
            cur.execute('DELETE FROM Marks where regd=? and sem=?',(regd,sem))            
        except:
            return render_template('error.html',e="Record not found")
        conn.commit()
        return redirect('/home')
    return render_template('delete.html')
@app.route('/home',methods=['GET','POST'])
def home():
    if session["user_id"]=="Admin":
        cur.execute('Select * from marks')
        l=cur.fetchall()
        return render_template('home.html',marks=l)
    else:
        c=session["user_id"]
        cur.execute('Select * from marks where regd=?',(c,))
        l=cur.fetchall()
        return render_template('home.html',marks=l)
if __name__ == '__main__':
    app.run(debug=True)
