# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import os

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from sqlalchemy import desc
from sqlalchemy.orm import backref

import config
from forms import *
from models import Artist, Venue, State, Genre, create_state, create_genre, Show, db, app

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#


db.create_all()
create_state()
create_genre()


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/', methods=['GET'])
def index():
    recently_artists = Artist.query.order_by(desc('id')).limit(10)
    recently_venues = Venue.query.order_by(desc('id')).limit(10)
    return render_template('pages/home.html',
                           recently_artists=recently_artists,
                           recently_venues=recently_venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues', methods=['GET'])
def venues():
    data = []
    areas = db.session.query(Venue.city, Venue.state_id).distinct()
    for area in areas:
        city = area.city
        state = area.state_id
        venues_list = Venue.query.filter_by(city=city, state_id=state).all()
        venue_data = []
        for venue in venues_list:
            venue_data.append({
                "id": venue.id,
                "name": venue.name,
            })
        data.append({
            "city": city,
            "state": State.query.get(state).code,
            "venues": venue_data
        })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term')
    venues = Venue.query.order_by(Venue.name)
    venues = venues.filter(Venue.name.ilike(f'%{search_term}%'))

    response = {
        "count": venues.count(),
        "data": venues
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>', methods=['GET'])
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)

    past_shows = db.session.query(
            Artist.id.label("artist_id"),
            Artist.name.label("artist_name"),
            Artist.image_link.label("artist_image_link"),
            Show.start_time
        ).filter(
            Show.venue_id == venue_id,
            Show.artist_id == Artist.id,
            Show.start_time < datetime.utcnow()
        ).all()

    upcoming_shows = db.session.query(
            Artist.id.label("artist_id"),
            Artist.name.label("artist_name"),
            Artist.image_link.label("artist_image_link"),
            Show.start_time
        ).filter(
            Show.venue_id == venue_id,
            Show.artist_id == Artist.id,
            Show.start_time > datetime.now()
        ).all()

    data = {
        "id": venue_id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm(request.form)
    form.genres.choices = [(g.id, g.name) for g in Genre.query.order_by('name').all()]
    form.state.choices = [(s.id, s.code) for s in State.query.order_by('code').all()]

    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)

    if form.validate_on_submit():
        try:
            venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state_id=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                website_link=form.website_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data
            )

            genres = []
            for genre_id in form.genres.data:
                genres.append(Genre.query.get(genre_id))

            venue.genres = genres

            for g in genres:
                g.venues = [venue]

            db.session.add(venue)
            db.session.commit()

            flash('Venue ' + form.name.data + ' was successfully listed!')
            return redirect(url_for('index'))
        except:
            db.session.rollback()
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
            return redirect(url_for('create_venue_submission'))
        finally:
            db.session.close()
    else:
        for field, errors in form.errors.items():  # https://stackabuse.com/flask-form-validation-with-flask-wtf/
            flash(field + ': ' + '|'.join(errors))

    return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id)
    try:
        for g in venue.genres:
            db.session.delete(g)

        for sh in venue.shows:
            db.session.delete(sh)
        db.session.delete(venue)
        db.session.commit()

        flash('Venue was successfully deleted!')
        return redirect(url_for('venues'))
    except Exception as e:
        print(e)
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be deleted.')
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = Artist.query.order_by('id').all()

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term')
    artist = Artist.query.order_by(Artist.name)
    artist = artist.filter(Artist.name.ilike(f'%{search_term}%'))

    response = {
        "count": artist.count(),
        "data": artist
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)

    past_shows = db.session.query(
            Venue.id.label("venue_id"),
            Venue.name.label("venue_name"),
            Venue.image_link.label("venue_image_link"),
            Show.start_time
        ).filter(
            Show.artist_id == artist_id,
            Show.venue_id == Venue.id,
            Show.start_time < datetime.now()
        ).all()

    upcoming_shows = db.session.query(
            Venue.id.label("venue_id"),
            Venue.name.label("venue_name"),
            Venue.image_link.label("venue_image_link"),
            Show.start_time
        ).filter(
            Show.artist_id == artist_id,
            Show.venue_id == Venue.id,
            Show.start_time > datetime.now()
        ).all()

    data = {
        "id": artist_id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(state=artist.state_id)
    form.genres.data = [g.id for g in artist.genres]
    form.genres.choices = [(g.id, g.name) for g in Genre.query.order_by('name').all()]
    form.state.choices = [(s.id, s.code) for s in State.query.order_by('code').all()]

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    if form.validate_on_submit():
        try:
            artist = Artist.query.get(artist_id)

            genres = []
            for genre_id in form.genres.data:
                genres.append(Genre.query.get(genre_id))
            artist.genres = genres

            for g in genres:
                g.artists = [artist]

            artist.name = form.name.data
            artist.city = form.city.data
            artist.state_id = form.state.data
            artist.phone = form.phone.data
            artist.facebook_link = form.facebook_link.data
            artist.image_link = form.image_link.data
            artist.website_link = form.website_link.data
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data

            db.session.commit()

            flash('Artist was successfully edited!')
            return redirect(url_for('show_artist', artist_id=artist_id))
        except:
            db.session.rollback()
            flash('An error occurred. Artist could not be edited.')
            return redirect(url_for('edit_artist', artist_id=artist_id))
        finally:
            db.session.close()
    else:
        for field, errors in form.errors.items():  # https://stackabuse.com/flask-form-validation-with-flask-wtf/
            flash(field + ': ' + '|'.join(errors))

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(state=venue.state_id)
    form.genres.data = [g.id for g in venue.genres]
    form.genres.choices = [(g.id, g.name) for g in Genre.query.order_by('name').all()]
    form.state.choices = [(s.id, s.code) for s in State.query.order_by('code').all()]

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    if form.validate_on_submit():
        try:
            venue = Venue.query.get(venue_id)

            genres = []
            for genre_id in form.genres.data:
                genres.append(Genre.query.get(genre_id))
            venue.genres = genres

            for g in genres:
                g.venues = [venue]

            venue.name = form.name.data
            venue.city = form.city.data
            venue.state_id = form.state.data
            venue.address = form.address.data
            venue.phone = form.phone.data
            venue.facebook_link = form.facebook_link.data
            venue.image_link = form.image_link.data
            venue.website_link = form.website_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data

            db.session.commit()

            flash('Venue was successfully edited!')
            return redirect(url_for('show_venue', venue_id=venue_id))
        except:
            db.session.rollback()
            flash('An error occurred. Venue could not be edited.')
            return redirect(url_for('edit_venue', venue_id=venue_id))
        finally:
            db.session.close()
    else:
        for field, errors in form.errors.items():  # https://stackabuse.com/flask-form-validation-with-flask-wtf/
            flash(field + ': ' + '|'.join(errors))
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    form.genres.choices = [(g.id, g.name) for g in Genre.query.order_by('name').all()]
    form.state.choices = [(s.id, s.code) for s in State.query.order_by('code').all()]
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)

    if form.validate_on_submit():
        try:
            artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state_id=form.state.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                website_link=form.website_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data
            )

            genres = []
            for genre_id in form.genres.data:
                genres.append(Genre.query.get(genre_id))

            artist.genres = genres

            for g in genres:
                g.artists = [artist]

            db.session.add(artist)
            db.session.commit()

            flash('Artist ' + form.name.data + ' was successfully listed!')
            return redirect(url_for('index'))
        except:
            db.session.rollback()
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
            return redirect(url_for('create_artist_form'))
        finally:
            db.session.close()
    else:
        for field, errors in form.errors.items():  # https://stackabuse.com/flask-form-validation-with-flask-wtf/
            flash(field + ': ' + '|'.join(errors))

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows_list = Show.query.order_by('start_time').all()
    data = []
    for sh in shows_list:
        item = {
            "venue_id": sh.venue_id,
            "venue_name": sh.venue.name,
            "artist_id": sh.artist_id,
            "artist_name": sh.artist.name,
            "artist_image_link": sh.artist.image_link,
            "start_time": str(sh.start_time)
        }
        data.append(item)
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)
    if form.validate_on_submit():
        try:
            show = Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data
            )

            db.session.add(show)
            db.session.commit()

            flash('Show was successfully listed!')
            return redirect(url_for('index'))
        except:
            db.session.rollback()
            flash('An error occurred. Show could not be listed.')
            return redirect(url_for('create_shows'))
        finally:
            db.session.close()
    else:
        for field, errors in form.errors.items():  # https://stackabuse.com/flask-form-validation-with-flask-wtf/
            flash(field + ': ' + '|'.join(errors))
    return redirect(url_for('create_shows'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# # Default port:
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port)
