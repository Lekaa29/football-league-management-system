from flask_login import UserMixin
from sqlalchemy.sql import func
from . import db 


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    leagues = db.relationship('League')
    
class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    
class League(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    teamCount = db.Column(db.Integer)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    seasons = db.relationship('Season')

class Season(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    league_id = db.Column(db.Integer, db.ForeignKey("league.id"))
    teams = db.relationship('Team')
    
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    stadium_name = db.Column(db.String(50))
    home_kit_first = db.Column(db.String(7), nullable=False)
    home_kit_second = db.Column(db.String(7), nullable=False)
    away_kit_first = db.Column(db.String(7), nullable=False)
    away_kit_second = db.Column(db.String(7), nullable=False)
    logo = db.Column(db.LargeBinary, default=lambda: b'<default_image_bytes>')
    season_id = db.Column(db.Integer, db.ForeignKey("season.id"))

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    number = db.Column(db.Integer)
    image = db.Column(db.LargeBinary, default=lambda: b'<default_image_bytes>')
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"))
