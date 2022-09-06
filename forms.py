from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class Find(FlaskForm):
    movie = StringField(label='Movie/Series Name')
    submit = SubmitField(label='Done')


class Epi(FlaskForm):
    episode = StringField(label='Enter episode numbers separated by "," or\nspecify start til end using 1-7 :')
    submit = SubmitField(label='Done')
