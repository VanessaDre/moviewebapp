from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    # One-to-many: a user has many movies
    movies = db.relationship("Movie", backref="user", cascade="all, delete-orphan")


class Movie(db.Model):
    __tablename__ = "movie"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    director = db.Column(db.String(200), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    poster_url = db.Column(db.String(500), nullable=True)

    # Link Movie to User
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
