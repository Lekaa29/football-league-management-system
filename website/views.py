from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, redirect, url_for
from .models import User, Tournament, League
from werkzeug.security import generate_password_hash, check_password_hash
from . import db 
from flask_login import login_user, login_required, logout_user, current_user

views = Blueprint('views', __name__)

@views.route('/')
def home():
    if current_user:
    
        return render_template("home.html", user=current_user.username)
    else:
        return render_template("main.html", user=current_user)
    
@views.route('/addleague', methods=["GET", "POST"])
@login_required
def addleague():
    if request.method == "GET":
        return render_template("addleague.html")
    else:
        leagueName = request.form.get("leaguename")
        teamCount = request.form.get("teamscount")
        
        user = current_user
        league = League.query.filter_by(name=leagueName).first()
        
        if league:
            return render_template("addleague.html", message="League name already in use!")
        else:
            new_league = League(name=leagueName, teamCount=teamCount)
            db.session.add(new_league)
            db.session.commit()
            
            return redirect(url_for("views.home"))
            
            
        
        
        
    