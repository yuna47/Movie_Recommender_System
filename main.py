import csv

from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func

from config import Config
from process_data import prepare_data
from recommend import recommend


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    preferred_genres = db.Column(db.String(255), default=' ')
    preferred_movies = db.Column(db.String(255), default=' ')


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(255), nullable=False)
    director = db.Column(db.String(255), nullable=False)
    actor = db.Column(db.Text, nullable=False)
    synopsis = db.Column(db.Text, nullable=False)
    img = db.Column(db.String(255), nullable=False)


@app.route('/')
def start():
    return render_template('start.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['user'] = {'id': user.id, 'username': user.username}

            user_info = session.get('user')
            user_id = user_info['id']
            user = User.query.get(user_id)

            preferred_genres_str = user.preferred_genres
            preferred_genres = preferred_genres_str.split()
            prepare_data(preferred_genres)

            return redirect(url_for('main'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('start'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if not username or not email or not password:
            return render_template('signUp.html', error='Please fill in all fields.')

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        session['user'] = {'id': new_user.id, 'username': new_user.username}

        return redirect(url_for('select_preferred_genres'))

    return render_template('signUp.html')


@app.route('/selectPreferredGenres', methods=['GET', 'POST'])
def select_preferred_genres():
    genres = ['코미디', '멜로/로맨스', '범죄', '액션', '드라마', '다큐멘터리', '스릴러', '공포(호러)',
              '미스터리', '어드벤처', '가족', '판타지', '뮤지컬', 'SF', '사극', '애니메이션']

    if request.method == 'POST':
        selected_genres = request.form.getlist('genre')

        user_info = session.get('user')
        user_id = user_info['id']
        user = User.query.get(user_id)

        user.preferred_genres = ' '.join(selected_genres)
        db.session.commit()

        return redirect(url_for('select_preferred_movies'))

    return render_template('select_preferred_genres.html', genres=genres)


@app.route('/selectPreferredMovies', methods=['GET', 'POST'])
def select_preferred_movies():
    movies = Movie.query.order_by(func.random()).limit(100).all()

    if request.method == 'POST':
        selected_movies_ids = request.form.getlist('movie')

        user_info = session.get('user')
        user_id = user_info['id']
        user = User.query.get(user_id)

        user.preferred_movies = ' '.join(selected_movies_ids)
        db.session.commit()

        user_info = session.get('user')
        user_id = user_info['id']
        user = User.query.get(user_id)

        preferred_genres_str = user.preferred_genres
        preferred_genres = preferred_genres_str.split()
        prepare_data(preferred_genres)

        return redirect(url_for('main'))

    return render_template('select_preferred_movies.html', movies=movies)


@app.route('/main')
def main():
    user_info = session.get('user')
    if user_info:
        username = user_info['username']
        user_id = user_info['id']
        user = User.query.get(user_id)

        preferred_movies_str = user.preferred_movies
        preferred_movies = list(map(int, preferred_movies_str.split()))

        preferred_genres_str = user.preferred_genres
        preferred_genres = preferred_genres_str.split()

        recommended_movie_ids = recommend(preferred_movies, preferred_genres, db.session.is_modified(user))
        recommended_movies = [Movie.query.get(movie_id) for movie_id in recommended_movie_ids]

        random_movies = Movie.query.order_by(func.random()).limit(20).all()

        return render_template('main.html', username=username, recommended_movies=recommended_movies, random_movies=random_movies)
    else:
        return redirect(url_for('login'))


@app.route('/allMovie')
def all_movie():
    movies = Movie.query.all()
    return render_template('allMovie.html',  movies=movies)


@app.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('search_query', '')

    if search_query:
        search_results = Movie.query.filter(Movie.title.ilike(f'%{search_query}%')).all()
    else:
        search_results = []

    return render_template('search_results.html', search_results=search_results, search_query=search_query)


@app.route('/main/<int:movie_id>')
def get_movie_details_main(movie_id):
    # SQLAlchemy를 사용하여 데이터베이스에서 영화 정보를 가져오기
    movie = Movie.query.get(movie_id)

    if movie:
        # 영화 정보가 있는 경우, 해당 정보를 HTML에 렌더링
        return render_template('movie_detail_modal.html', movie=movie)
    else:
        # 영화 정보가 없는 경우, 에러 메시지 또는 기본 정보를 반환
        return "영화 정보를 찾을 수 없습니다."


@app.route('/allMovie/<int:movie_id>')
def get_movie_details(movie_id):
    # SQLAlchemy를 사용하여 데이터베이스에서 영화 정보를 가져오기
    movie = Movie.query.get(movie_id)

    if movie:
        # 영화 정보가 있는 경우, 해당 정보를 HTML에 렌더링
        return render_template('movie_detail_modal.html', movie=movie)
    else:
        # 영화 정보가 없는 경우, 에러 메시지 또는 기본 정보를 반환
        return "영화 정보를 찾을 수 없습니다."


# @app.route('/movieDetails/<int:data_movie_id>')
# def movieDetails(data_movie_id):
#     # 해당 ID의 영화를 찾음
#     return render_template('movieDetails.html', movie_id=data_movie_id)


# CSV 파일에서 데이터를 읽어와 데이터베이스에 삽입하는 함수
# @app.route('/')
def insert_data_from_csv(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            # CSV 파일에서 읽어온 각 행을 데이터베이스에 삽입
            movie = Movie(title=row['title'], genre=row['genre'], director=row['director'],
                          actor=row['actor'], synopsis=row['synopsis'], img=row['img'])
            db.session.add(movie)

        # 변경사항을 데이터베이스에 커밋
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # 데이터베이스가 비어있을 경우에만 CSV 파일에서 데이터 삽입
        if not Movie.query.first():
            insert_data_from_csv('./movie_crawl/output/movie.csv')
    app.run(debug=True)
