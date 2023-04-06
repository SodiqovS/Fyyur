import csv

from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import now

import config

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Genre(db.Model):
    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __repr__(self):
        return f"<Genre {self.id}>"

    def __str__(self):
        return self.name


def create_genre():
    if Genre.query.count() == 0:
        with open('genres.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                db.session.add(Genre(name=row[0]))

        db.session.commit()


class State(db.Model):
    __tablename__ = 'states'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(2))

    def __repr__(self):
        return f"<State {self.id}>"

    def __str__(self):
        return self.code


def create_state():
    if State.query.count() == 0:
        with open('states.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                db.session.add(State(code=row[0]))

        db.session.commit()


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state_id = db.Column(db.Integer, db.ForeignKey('states.id'), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.Text)

    genres = db.relationship("Genre", secondary="venue_genre", backref="venues")
    shows = db.relationship('Show', backref='venue')
    state = db.relationship('State', backref='venues')

    def __repr__(self):
        return f"<Venue {self.id}>"

    def __str__(self):
        return self.name


venue_genre = db.Table(
    "venue_genre",
    db.Column("venue_id", db.ForeignKey("venues.id"), primary_key=True),
    db.Column("genre_id", db.ForeignKey("genres.id"), primary_key=True)
)


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state_id = db.Column(db.Integer, db.ForeignKey('states.id'), nullable=False)
    phone = db.Column(db.String(20))
    genres = db.relationship("Genre", secondary="artist_genre", backref="artists")
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.Text)

    shows = db.relationship('Show', backref='artist')
    state = db.relationship('State', backref='artists')

    def __repr__(self):
        return f"<Artist {self.id}>"

    def __str__(self):
        return self.name


artist_genre = db.Table(
    "artist_genre",
    db.Column("artist_id", db.ForeignKey("artists.id"), primary_key=True),
    db.Column("genre_id", db.ForeignKey("genres.id"), primary_key=True)
)


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f"<Show {self.id}>"
