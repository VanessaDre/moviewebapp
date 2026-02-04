import os

import requests
from flask import Flask, redirect, render_template, request, url_for

from data_manager import DataManager
from models import db, Movie

app = Flask(__name__)

# --- Database (robust absolute path) ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "moviewebapp.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

data_manager = DataManager()


def fetch_movie_from_omdb(title: str) -> dict | None:
    api_key = os.environ.get("OMDB_API_KEY")
    if not api_key:
        return None

    url = "https://www.omdbapi.com/"
    params = {"t": title, "apikey": api_key}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if data.get("Response") != "True":
        return None

    return data


@app.route("/")
def index():
    users = data_manager.get_users()
    return render_template("index.html", users=users)


@app.route("/users", methods=["POST"])
def create_user():
    name = request.form.get("name", "").strip()
    if name:
        data_manager.create_user(name)
    return redirect(url_for("index"))


@app.route("/users/<int:user_id>/movies", methods=["GET"])
def user_movies(user_id: int):
    users = data_manager.get_users()
    user = next((u for u in users if u.id == user_id), None)
    if not user:
        return redirect(url_for("index"))

    movies = data_manager.get_movies(user_id)
    return render_template("movies.html", user=user, movies=movies)


@app.route("/users/<int:user_id>/movies", methods=["POST"])
def add_movie(user_id: int):
    title = request.form.get("title", "").strip()
    if not title:
        return redirect(url_for("user_movies", user_id=user_id))

    try:
        omdb_data = fetch_movie_from_omdb(title)
    except Exception:
        omdb_data = None

    if not omdb_data:
        return redirect(url_for("user_movies", user_id=user_id))

    director = omdb_data.get("Director")
    year_raw = omdb_data.get("Year")
    poster_url = omdb_data.get("Poster")

    year = None
    if year_raw and year_raw.isdigit():
        year = int(year_raw)

    if poster_url == "N/A":
        poster_url = None

    movie = Movie(
        name=omdb_data.get("Title", title),
        director=None if director in (None, "N/A") else director,
        year=year,
        poster_url=poster_url,
        user_id=user_id,
    )

    data_manager.add_movie(movie)
    return redirect(url_for("user_movies", user_id=user_id))


@app.route("/users/<int:user_id>/movies/<int:movie_id>/update", methods=["POST"])
def update_movie(user_id: int, movie_id: int):
    new_title = request.form.get("new_title", "").strip()
    if new_title:
        data_manager.update_movie(movie_id, new_title)
    return redirect(url_for("user_movies", user_id=user_id))


@app.route("/users/<int:user_id>/movies/<int:movie_id>/delete", methods=["POST"])
def delete_movie(user_id: int, movie_id: int):
    data_manager.delete_movie(movie_id)
    return redirect(url_for("user_movies", user_id=user_id))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5002)
