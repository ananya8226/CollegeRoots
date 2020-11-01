from flask import Flask, render_template, url_for, request, redirect, session, logging, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import sqlite3
from datetime import datetime
from passlib.hash import sha256_crypt

app = Flask(__name__)
basepath = ""
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+basepath+'blog.db'
app.config['SQLALCHEMY_BINDS'] = {'teo': 'sqlite:///'+basepath+'teo.db',
                                  'reg': 'sqlite:///'+basepath+'reg.db'}


app.config['SECRET_KEY'] = '683573db5e9b59731aaccb1f2ded7a86'

db = SQLAlchemy(app)


class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)


class teo(db.Model):
    __bind_key__ = 'teo'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)


class reg(db.Model):
    __bind_key__ = 'reg'
    id = db.Column(db.Integer, primary_key=True)
    collegename = db.Column(db.String(50))
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(20))


@app.route("/open-to-all")
def opentoall():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    return render_template('open-to-all.html', posts=posts)


@app.route("/college-specific")
def collegespecific():
    posts = teo.query.order_by(teo.date_posted.desc()).all()
    return render_template('college-specific.html', posts=posts)


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/register")
def register():
    return render_template('register.html')


@app.route("/login")
def login():
    return render_template('login.html')


@app.route("/option")
def option():
    return render_template('option.html')


@app.route('/post/<int:post_id>')
def post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()

    return render_template('post.html', post=post)


@app.route('/post1/<int:post_id>')
def post1(post_id):
    post = teo.query.filter_by(id=post_id).one()

    return render_template('post1.html', post=post)


@app.route('/add')
def add():
    return render_template('add.html')


@app.route('/addpost', methods=['POST'])
def addpost():
    title = request.form['title']
    subtitle = request.form['subtitle']
    author = request.form['author']
    content = request.form['content']

    post = Blogpost(title=title, subtitle=subtitle, author=author,
                    content=content, date_posted=datetime.now())

    db.session.add(post)
    db.session.commit()

    return redirect(url_for('opentoall'))


@app.route('/add1')
def add1():
    return render_template('add1.html')


@app.route('/addpost1', methods=['POST'])
def addpost1():
    title = request.form['title']
    subtitle = request.form['subtitle']
    author = request.form['author']
    content = request.form['content']

    if subtitle == "MMMUT":
        post = teo(title=title, subtitle=subtitle, author=author,
                   content=content, date_posted=datetime.now())
    else:
        return redirect(url_for('collegespecific'))

    db.session.add(post)
    db.session.commit()

    return redirect(url_for('collegespecific'))


@app.route("/registration", methods=['POST'])
def registration():
    conn = sqlite3.connect(basepath+'reg.db')
    cc = conn.cursor()
    signup = request.form
    collegename = signup['collegename']
    name = signup['name']
    email = signup['email']
    password = signup['password']

    cc.execute("INSERT INTO reg(collegename, name, email, password) VALUES(:collegename, :name, :email, :password)",
               {"collegename": collegename, "name": name, "email": email, "password": password})
    conn.commit()

    return redirect(url_for('option'))


@app.route('/login_validation', methods=['POST'])
def login_validation():
    conn = sqlite3.connect(basepath+'reg.db')
    cc = conn.cursor()
    email = request.form['email']
    password = request.form['password']

    emaildata = cc.execute("SELECT email FROM reg WHERE email=:email", {
                           "email": email}).fetchone()
    passworddata = cc.execute("SELECT password FROM reg WHERE email=:email", {
                              "email": email}).fetchone()

    if emaildata is not None:
        for password_data in passworddata:
            if password == password_data:
                return redirect(url_for('option'))
    else:
        return redirect(url_for('login'))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    app.run(debug=True)
