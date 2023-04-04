from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, HiddenField
from wtforms.validators import DataRequired, URL, regexp


class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id',
        validators=[DataRequired(), regexp(regex=r'^[1-9]\d*$|^0$', message='ID only accepts integers!')]
    )
    venue_id = StringField(
        'venue_id',
        validators=[DataRequired(), regexp(r'^[1-9]\d*$|^0$', message='ID only accepts integers!')]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default=datetime.today()
    )
    csrf_token = HiddenField()


class VenueForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state',
        validators=[DataRequired()],
        choices=[],
        validate_choice=False,
        coerce=int
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=[],
        validate_choice=False,
        coerce=int
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website_link = StringField(
        'website_link'
    )

    seeking_talent = BooleanField('seeking_talent')

    seeking_description = StringField(
        'seeking_description'
    )
    csrf_token = HiddenField()


class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[],
        validate_choice=False,
        coerce=int
    )
    phone = StringField(
        'phone',
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=[],
        validate_choice=False,
        coerce=int
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )

    website_link = StringField(
        'website_link', validators=[URL()]
    )

    seeking_venue = BooleanField('seeking_venue')

    seeking_description = StringField(
        'seeking_description'
    )
    csrf_token = HiddenField()
