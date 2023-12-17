from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, redirect, url_for
from .models import User, Tournament, League, Season
from werkzeug.security import generate_password_hash, check_password_hash
from . import db 
from flask_login import login_user, login_required, logout_user, current_user
import json
views = Blueprint('views', __name__)


@views.route('/')
def welcome():
    
    return render_template("main.html")
    

@views.route('/home')
@login_required
def home():
    return render_template("home.html", user=current_user)
   
    
@views.route('/addleague', methods=["GET", "POST"])
@login_required
def addleague():
    if request.method == "GET":
        return render_template("addleague.html", user=current_user)
    else:
        leagueName = request.form.get("leaguename")
        teamCount = request.form.get("teamscount")
        
        user = current_user
        league = League.query.filter_by(name=leagueName, user_id=current_user.id).first()
        
        if league:
            return render_template("addleague.html", user=current_user, message="League name already in use!")
        else:
            new_league = League(name=leagueName, teamCount=teamCount, user_id=current_user.id)
            db.session.add(new_league)
            db.session.commit()

            return redirect(url_for("views.home"))
            
            
@views.route("/league-main", methods=["GET","POST"])  
def edit_league():
    
    league_id = request.form['leagueid']
    league = League.query.get(league_id)
    seasons = Season.query.get(league_id)
    print(seasons)
    if seasons:
        return render_template("leaguemain.html", seasons=seasons, user=current_user,league=league)
    else:
        return render_template("add-season.html", user=current_user, league=league)
   
    
@views.route("/add-season", methods=["GET", "POST"])  
def add_season():
    if request.method == "POST":
        print(request.form)
        league_id = request.form["league_id"]
        name = request.form["name"]
        new_season = Season(name=name, league_id=league_id)
        db.session.add(new_season)
        db.session.commit()
        
        league = League.query.get(league_id)
        seasons = Season.query.get(league_id)
        
        return render_template("leaguemain.html", seasons=seasons, user=current_user,league=league)
    if request.method == "GET":
        print(1,request.form,1)
        league_id = request.form('league_id')
        print("aaaa:",league_id)
        league = League.query.get(league_id)
        return render_template("add-season.html", user=current_user, league=league)
   

        
    
        
    