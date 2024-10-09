from flask_login import UserMixin
from sqlalchemy.sql import func
from . import db 
from sqlalchemy import ForeignKeyConstraint

class TeamTableStats:
    def __init__(self, team_name, goals_scored=0, goals_conceded=0, wins=0, losses=0, draws=0):
        self.team_name = team_name
        self.goals_scored = goals_scored
        self.goals_conceded = goals_conceded
        self.wins = wins
        self.losses = losses
        self.draws = draws
        
class PlayerStats:
    def __init__(self, player_name, goals_scored=0):
        self.player_name = player_name
        self.goals_scored = goals_scored

        
