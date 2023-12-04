import csv
import os
import secrets
from tkinter import Image

from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://dc2023:dc5555@localhost:3306/movieflix'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(255), nullable=False)
    director = db.Column(db.String(255), nullable=False)
    actor = db.Column(db.Text, nullable=False)
    synopsis = db.Column(db.Text, nullable=False)
    img = db.Column(db.String(255), nullable=False)



@app.route('/allMovie')
def allMovie():
    movie = Movie.query.all()
    return render_template('allMovie.html',  movie=movie)


@app.route('/main')
def main():
    user_info = session.get('user')
    if user_info:
        username = user_info['username']
        return render_template('main.html', username=username)
    else:
        # 사용자 정보가 없으면 로그인 페이지로 리다이렉션
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['user'] = {'id': user.id, 'username': user.username}
            return redirect(url_for('main'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/logout')
def logout():
    pass


@app.route('/')
def start():
    return render_template('start.html')


@app.route('/signup', methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if not username or not email or not password:
            return render_template('signup.html', error='Please fill in all fields.')

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/movieDetails/<int:data_movie_id>')
def movieDetails(data_movie_id):
    # 해당 ID의 영화를 찾음
    return render_template('movieDetails.html', movie_id=data_movie_id)

@app.route('/myfavoGenre')
def myGenre():
    return render_template('my_genre_taste.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
