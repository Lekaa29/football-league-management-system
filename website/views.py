from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, redirect, url_for
from .models import User, Tournament, League, Season, Team, Player, Match, Goal
from werkzeug.security import generate_password_hash, check_password_hash
from . import db 
from flask_login import login_user, login_required, logout_user, current_user
import json
import base64



views = Blueprint('views', __name__)


@views.route('/')
def welcome():
    
    return render_template("main.html")
    

@views.route('/home')
def home():
    return render_template("home.html", user=current_user)
   
    
@views.route('/addleague', methods=["GET", "POST"])
def addleague():
    if request.method == "GET":
        league_id = request.args.get("league_id")
        season_id = request.args.get("season_id")
        return render_template("addleague.html", user=current_user, league_id=league_id, season_id=season_id)
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
        
@views.route('/addteam', methods=["GET", "POST"])
def addteam():
    if request.method == "GET":
        league_id = request.args.get("league_id")
        season_id = request.args.get("season_id")
        return render_template("addteam.html", user=current_user, league_id=league_id, season_id=season_id)
    else:
        league_id = request.form.get("league_id")
        season_id = request.form.get("season_id")
        
        
        
        teamName = request.form.get("team_name")
        stadiumName = request.form.get("stadium_name")
        homeKitFirst = request.form.get("home_kit_primary_color")
        homeKitSecond = request.form.get("home_kit_secondary_color")
        awayKitFirst = request.form.get("away_kit_primary_color")
        awayKitSecond = request.form.get("away_kit_secondary_color")
        
        image_data = None
        
        if 'image' in request.files:
            image_file = request.files['image']  # Use square brackets, not parentheses
            image_data = image_file.read()
            image_data= base64.b64encode(image_data)
                
        
        new_team = Team(name=teamName, stadium_name=stadiumName, home_kit_first=homeKitFirst, home_kit_second=homeKitSecond, away_kit_first=awayKitFirst, away_kit_second=awayKitSecond, logo=image_data, season_id=season_id)
        
        
        db.session.add(new_team)
        db.session.commit()
        
        team_id = new_team.id
        print("teamid: ", team_id)
        
        player_names = request.form.getlist('player_name[]')
        player_surnames = request.form.getlist('player_surname[]')
        player_numbers = request.form.getlist('player_number[]')
        
        if len(player_names) != len(player_surnames) or len(player_surnames) != len(player_numbers):
            return render_template("addteam.html", message="Please fill out all player fields!", user=current_user, league_id=league_id, season_id=season_id)
        else:
            for name, surname, number in zip(player_names, player_surnames, player_numbers):
                new_player = Player(name=name, surname=surname, number=number, team_id=team_id)
                db.session.add(new_player)
                db.session.commit()
                
                
        league = League.query.get(league_id)
        seasons = Season.query.get(league_id)
        
        return render_template("leaguemain.html", seasons=seasons, user=current_user,league=league) 
  
@views.route("/team-main", methods=["GET", "POST"])
def team_main():
    if request.method == "POST":
        
        teamid = request.form.get("team_id")
        leagueid = request.form.get("league_id")
        seasonid  = request.form.get("season_id")  
        
        team = Team.query.filter_by(id=teamid).all()
        print(0,teamid)
        print(0,leagueid)
        print(0,seasonid)
        players = Player.query.filter_by(team_id=teamid).all()
        
        #for player in players:
        #   print(2, player.team_id)
        
        print("xxxx")
        return render_template("team-main.html", user=current_user, players=players, team=team, leagueid=leagueid, seasonid=seasonid)

    else:
        season = request.form["season"]
        league_id= request.form["league_id"]
        
        league = League.query.get(league_id)
        seasons = Season.query.get(league_id)
        
        return render_template("leaguemain.html", season=season,  seasons=seasons, user=current_user,league=league)
    
@views.route("/player-main", methods=["POST"])
def player_main():
    if request.method == "POST":
        #teamid = request.form.get("team_id")
        #leagueid = request.form.get("league_id")
        #seasonid  = request.form.get("season_id") 
        playerid = request.form.get("player_id")
        
        player = Player.query.get(playerid)
        teamid = player.team_id
        team = Team.query.get(teamid)
        
        return render_template("player-main.html",user=current_user, player=player, team=team)
        
        
        
        
        
@views.route("/league-main", methods=["GET","POST"])  
def edit_league():
    
    league_id = request.form['leagueid']
    league = League.query.get(league_id)
    seasons = Season.query.get(league_id)

    matches = Match.query.filter_by(gameweek=1).all()
    
   # db.session.query(Match).delete()
    #db.session.commit()
    
    
    if seasons:
        teams = Team.query.get(seasons.id)
        
        images = []
        names = []
        for team in seasons.teams:
            images.append(team.logo)
            names.append(team.name)
           
        images = images[-1]
        names = names[-1]
        
        
        return render_template("leaguemain.html", matches=matches, images=images, teams=teams, seasons=seasons, user=current_user,league=league)
    else:
        return render_template("add-season.html", user=current_user, league=league)
   
    
@views.route("/add-season", methods=["GET", "POST"])  
def add_season():
    if request.method == "POST":
        league_id = request.form["league_id"]
        name = request.form["name"]
        new_season = Season(name=name, league_id=league_id)
        db.session.add(new_season)
        db.session.commit()
        
        league = League.query.get(league_id)
        seasons = Season.query.get(league_id)
        
        return render_template("leaguemain.html", seasons=seasons, user=current_user,league=league)
    if request.method == "GET":
        league_id = request.args.get("league_id")
        league = League.query.get(league_id)
        return render_template("add-season.html", user=current_user, league=league)
   

    
@views.route("/change-season", methods=["POST"])  
def change():
    if request.method == "POST":
        season = request.form["season"]
        league_id= request.form["league_id"]
        
        league = League.query.get(league_id)
        seasons = Season.query.get(league_id)
        
        return render_template("leaguemain.html", season=season,  seasons=seasons, user=current_user,league=league)
    
        

@views.route("/addresult", methods=["GET", "POST"])
def add_result():
    if request.method == "GET":
        league_id = request.args.get("league_id")
        season_id = request.args.get("season_id")
        
        teams = Team.query.filter_by(season_id=season_id).all()
        
        all_players=[]
        
        for team in teams:
            players_per_team = Player.query.filter_by(team_id=team.id).all()
            
            team_players = []
            for player in players_per_team:
                print(0,player.name)
                player_dict = {
                'number': player.number,
                'name': player.name,
                'surname': player.surname
                }
                team_players.append(player_dict)
            
            all_players.append(team_players)

        
        
        return render_template("add_result.html", players=all_players, user=current_user, league_id=league_id, season_id=season_id, teams=teams)
    else:
        print(request.form)
        leagueid = request.form.get("league_id")
        seasonid  = request.form.get("season_id")  
        
        team1_id = request.form.get("football-team1")
        team2_id = request.form.get("football-team2")
        
        gameweek = request.form.get("gameweek")
        
        
       
        
        team1_goals = request.form.get("team1_goals")
        team2_goals = request.form.get("team2_goals")
        
       
        team1_scorers = request.form.getlist("team1_scorers")
        team2_scorers = request.form.getlist("team2_scorers")

        print(team1_scorers)
        print()
        print(team2_scorers)
        
        
        match = Match(gameweek=int(gameweek), team_home_id=team1_id, team_away_id=team2_id, season_id=seasonid, scored_home=team1_goals, scored_away=team2_goals)
        db.session.add(match)
        db.session.commit()
        
        
        players1 = Player.query.filter_by(team_id=team1_id).all()
        
        c = 0
        for player in players1:
            print(player.name)
            print(team1_scorers)
            if team1_scorers[c]:
                
                goal = Goal(amount=team1_scorers[c], scorer_id=player.id, match_id=match.id, team_id=team1_id)
                db.session.add(goal)
                db.session.commit()
            c+=1
        
        print()
        c = 0
        players2 = Player.query.filter_by(team_id=team2_id).all()
        for player in players2:
            print(player.name)
            if team2_scorers[c]:
                goal = Goal(amount=team1_scorers[c], scorer_id=player.id, match_id=match.id, team_id=team2_id)
                db.session.add(goal)
                db.session.commit()
            c+=1
        
        league = League.query.get(leagueid)
        seasons = Season.query.get(seasonid)
        return render_template("leaguemain.html",  seasons=seasons, user=current_user,league=league)

    
    
    
    
@views.route("/removeteam", methods=["POST"])
def remove_team():
    team_id = request.form["team_id"]
    
    print(192392131,team_id)
    team = Team.query.get(int(team_id))
    

    if team:
            try:
                db.session.delete(team)
                players_to_remove = Player.query.filter_by(team_id=team_id).all()
                for player in players_to_remove:
                    db.session.delete(player)
                db.session.commit()
                print(f"Team with ID {team_id} has been successfully removed.")
            except Exception as e:
                db.session.rollback()
                print(f"Error occurred while removing team with ID {team_id}: {str(e)}")
    else:
        print(f"No team found with ID {team_id}")
  
    
    league_id = request.form["league_id"]
    season_id = request.form["season_id"]
  
    league = League.query.get(league_id)
    seasons = Season.query.get(season_id)
    
    
    return render_template("leaguemain.html", seasons=seasons, user=current_user,league=league)


@views.route("/match-main", methods=["POST"])
def match_main():
   
    league_id = request.form["league_id"]
    season_id = request.form["season_id"]
    match_id = request.form["match_id"]
    
    match = Match.query.get(match_id)
    seasons = Season.query.get(season_id)
    league_id = request.form["league_id"]
    
    goals_home = Goal.query.filter_by(match_id=match.id, team_id=match.team_home_id).all()
    goals_away = Goal.query.filter_by(match_id=match.id, team_id=match.team_away_id).all()
    
    goals_print = Goal.query.filter_by(match_id=match.id, ).all()
    print("goals:", goals_print)
    
    scorers_home = []
    scorers_away = []
   
    
    
    
    return render_template("match_main.html", match=match, user=current_user, league_id=league_id, season_id=season_id)
