from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, redirect, url_for
from .models import User, Tournament, League, Season, Team, Player, Match, Goal
from werkzeug.security import generate_password_hash, check_password_hash
from . import db 
from flask_login import login_user, login_required, logout_user, current_user
import json
import base64
from .classes import TeamTableStats, PlayerStats
from sqlalchemy import and_, or_

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
        
        
        return redirect(url_for('views.edit_league', leagueid=league.id))

      
  
@views.route("/team-main", methods=["GET", "POST"])
def team_main():
    if request.method == "GET":
        
        teamid = request.args.get("team_id")
        leagueid = request.args.get("league_id")
        seasonid  = request.args.get("season_id")  
        
        team = Team.query.filter_by(id=teamid).first()
        print(0,teamid)
        print(0,leagueid)
        print(0,seasonid)
        
        print(team)
        
        players = Player.query.filter_by(team_id=teamid).all()
        
        #for player in players:
        #   print(2, player.team_id)
        
        table_history = []
        
        teamCount = Team.query.filter_by(season_id=seasonid).count()
        teamCount = int(teamCount)
        
        league = League.query.filter_by(id=leagueid).first
        teams = {}
        print(teamCount)
        for i in range (1, (teamCount)*2):
            matches = Match.query.filter(
            and_(
                    Match.gameweek == i, Match.season_id == seasonid
                )
            ).all()
            
            if len(matches) == 0:
                break
            
            for match in matches:
                scored = match.scored_home
                conceded = match.scored_away
                wins = int(match.scored_home > match.scored_away)
                draws = int(match.scored_home == match.scored_away)
                losses = int(match.scored_home < match.scored_away)
                
                if match.team_home_id in teams:
                    scored += teams[match.team_home_id].goals_scored 
                    conceded += teams[match.team_home_id].goals_conceded 
                    wins += teams[match.team_home_id].wins
                    draws += teams[match.team_home_id].draws
                    losses += teams[match.team_home_id].losses 
                
                teams[match.team_home_id] = TeamTableStats(match.team_home.name, scored, conceded, wins, losses, draws)
                
                
                scored = match.scored_away
                conceded = match.scored_home
                wins = int(match.scored_home < match.scored_away)
                draws = int(match.scored_home == match.scored_away)
                losses = int(match.scored_home > match.scored_away)
                
                if match.team_away_id in teams:
                    scored += teams[match.team_away_id].goals_scored 
                    conceded += teams[match.team_away_id].goals_conceded 
                    wins += teams[match.team_away_id].wins
                    draws += teams[match.team_away_id].draws
                    losses += teams[match.team_away_id].losses  
                    
                teams[match.team_away_id] = TeamTableStats(match.team_away.name, scored, conceded, wins, losses, draws)
                

            teams_list = sorted(teams.values(), key=lambda team: (team.wins * 3 + team.draws, team.goals_scored - team.goals_conceded), reverse=True)


            print("id", teamid)
            if int(teamid) in teams:
                position = teams_list.index(teams[int(teamid)]) + 1
            else:
                teams_all = Team.query.filter_by(season_id=seasonid).all()
                position = len(teams_all)
            table_history.append(position)

            
        gw_results = []
        
        teamCount = Team.query.filter_by(season_id=seasonid).count()
        teamCount = int(teamCount)
            
        for i in range (1, (teamCount-1)*2):
            gw_matches = Match.query.filter(
            and_(
                    or_(Match.team_home_id == teamid, Match.team_away_id == teamid),
                    Match.gameweek == i
                )
            ).all()
            
            
            for x in gw_matches:
                outcome = 0
                
                print(x.team_home_id, teamid, x.team_away_id)
                if int(x.team_home_id) == int(teamid):
                    if x.scored_home > x.scored_away:
                        outcome = 1
                    if x.scored_home < x.scored_away:
                        outcome = -1
                    if x.scored_home == x.scored_away:
                        outcome = 0
                if int(x.team_away_id) == int(teamid):
                    if x.scored_home > x.scored_away:
                        outcome = -1
                    if x.scored_home < x.scored_away:
                        outcome = 1
                    if x.scored_home == x.scored_away:
                        outcome = 0  
                
                 #0draw 1 win -1 loss
                
                
                gw_results.append([i,outcome,x, int(teamid)])
        
        
        
        players_goals = {}
        all_team_matches = Match.query.filter(
            or_(Match.team_home_id == teamid, Match.team_away_id == teamid)
            ).all()
        
        
        for match in all_team_matches:
            for goal in match.goal_home:
                if int(goal.team_id) == int(teamid):
                    players_goals[goal.scorer_id] = goal.amount + players_goals.get(goal.scorer_id, 0)
            
        players_stats = []
        for player_id, goals_scored in players_goals.items():
            player = Player.query.get(player_id)
            if player:
                name = f"{player.name} {player.surname}"
                players_stats.append(PlayerStats(name, goals_scored))
                
        
            
            
        gw_results.reverse()    
            
        
        return render_template("team-main.html", players_stats=players_stats, gw_results=gw_results, teams_count=len(teams_list), chart_data=table_history, user=current_user, players=players, team=team, leagueid=leagueid, seasonid=seasonid)

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
        leagueid = request.form.get("league_id")
        seasonid  = request.form.get("season_id") 
        playerid = request.form.get("player_id")
        
        player = Player.query.get(playerid)
        teamid = player.team_id
        team = Team.query.get(teamid)
        league = League.query.get(leagueid)
        
        all_goals = Goal.query.filter(Goal.scorer_id==player.id).all()
        
        games_count = len(all_goals)
        gameids_scored = {}
        goals_count = 0
        for goal in all_goals:
            goals_count += goal.amount
            gameids_scored[int(goal.match_id)] = goal.amount
        
        gw_results = []
        
        teamCount = Team.query.filter_by(season_id=seasonid).count()
        teamCount = int(teamCount)
        
        for i in range (1, (teamCount-1)*2):
            gw_matches = Match.query.filter(
            and_(
                    or_(Match.team_home_id == teamid, Match.team_away_id == teamid),
                    Match.gameweek == i
                )
            ).all()
            
            scored = 0
            
            for x in gw_matches:
                if int(x.id) in gameids_scored.keys():
                    scored = gameids_scored[int(x.id)]
                gw_results.append([i,x, int(teamid), scored])
        
        
        gw_results.reverse()    
        
        return render_template("player-main.html", gw_results=gw_results,games_count=games_count, goals_count=goals_count,user=current_user, player=player, team=team)
        
    
@views.route("/addplayer", methods=["GET", "POST"])
def add_player():
    if request.method == "GET":
        
        leagueid = request.args.get("league_id")        
        seasonid = request.args.get("season_id")
        teamid = request.args.get("team_id")  
        print(leagueid)
        league = League.query.get(leagueid)
        season = Season.query.get(seasonid)
        team = Team.query.get(teamid)
        
        return render_template("add_player.html", user=current_user,leagueid=leagueid, seasonid=seasonid, teamid=teamid)
    else:
        leagueid = request.form["leagueid"]        
        seasonid = request.form["seasonid"]
        teamid = request.form["teamid"] 
        player_name = request.form["player_name"]
        player_surname = request.form["player_surname"]
        shirt_number = request.form["shirt_number"]
        
        player_number = Player.query.filter(
            and_(Player.number == shirt_number,
                 Player.team_id == teamid
                )
            ).all()
        print(shirt_number, player_number)
        if len(player_number) > 0:
            return render_template("add_player.html",  user=current_user,leagueid=leagueid, seasonid=seasonid, teamid=teamid, message="Player number taken!")
 
        league = League.query.get(leagueid)
        season = Season.query.get(seasonid)
        team = Team.query.get(teamid)
        
        new_player = Player(name=player_name, surname=player_surname, number=shirt_number, team_id=teamid)
        db.session.add(new_player)
        db.session.commit()
        
        return redirect(url_for('views.team_main', season_id=seasonid, league_id=leagueid, team_id=teamid))
        
        
        
        
        
        
@views.route("/league-main", methods=["GET","POST"])  
def edit_league():
    
    league_id = request.args.get('leagueid')
    season_id = request.args.get('season_id')
    season_selected_index = request.args.get('season_index')
    
    if season_id:
         season = Season.query.filter_by(id=season_id).first()
    else:
         season = Season.query.filter_by(league_id=league_id).first()

    if not league_id:
        league_id = season.league_id

    league = League.query.get(league_id)
    seasons = Season.query.filter_by(league_id=league_id).all()
    print("l:id",league_id)
    print("s:id",season_id)

    teamCount = Team.query.filter_by(season_id=season_id).count()
    teamCount = int(teamCount)
    
    gameweeks = []
    print("team count", teamCount)
    for i in range(1, teamCount):
        gameweek = Match.query.filter(
            and_(
                    Match.gameweek == i, Match.season_id == season_id
                )
            ).all()
        gameweeks.append(gameweek)
        print(gameweek)
    
    #matches = Match.query.filter_by(gameweek=1).all()
    
   # db.session.query(Match).delete()
    #db.session.commit()
    
    teams_stats = []
    
    teams = Team.query.filter_by(season_id=season.id).all()
        
    players = {}

    all_matches = Match.query.filter_by(season_id=season.id).all()

    for match in all_matches:
        for goal in match.goal_home:
            players[goal.scorer_id] = goal.amount + players.get(goal.scorer_id, 0)
        
    players_stats = []
    for player_id, goals_scored in players.items():
        player = Player.query.get(player_id)
        if player:
            name = f"{player.name} {player.surname}"
            players_stats.append(PlayerStats(name, goals_scored))
            
        
    
    players_stats = sorted(players_stats, key=lambda player: player.goals_scored, reverse=True)
    
    for team in teams:
        team_matches = Match.query.filter(
            and_(
                    or_(Match.team_home_id == team.id, Match.team_away_id == team.id),
                    Match.season_id == season.id
                )
            ).all()
        
        scored = 0
        conceded = 0
        wins = 0
        losses = 0
        draws = 0
        
        for match in team_matches:
            if match.team_home_id == team.id:
                scored += match.scored_home
                conceded += match.scored_away
                
                if(match.scored_home > match.scored_away):
                    wins +=1
                elif(match.scored_home < match.scored_away):
                    losses += 1
                else:
                    draws += 1
            else:
                scored += match.scored_away
                conceded += match.scored_home
                
                if(match.scored_home > match.scored_away):
                    losses +=1
                elif(match.scored_home < match.scored_away):
                    wins += 1
                else:
                    draws += 1
                    
            
    
        teams_stats.append(TeamTableStats(team_name=team.name, goals_scored=scored, goals_conceded=conceded, wins=wins, losses=losses, draws=draws))
    
    teams_stats = sorted(teams_stats, key=lambda team: (team.wins * 3 + team.draws, team.goals_scored - team.goals_conceded), reverse=True)

    
    
    
    
    if seasons:
        
        print("selected index:",season_selected_index)
        if not season_selected_index:
            season_selected_index = 1
        season_selected_index = int(season_selected_index)
        return render_template("leaguemain.html", season_selected_index=season_selected_index,players_stats=players_stats, teams_stats=teams_stats, gameweeks=gameweeks, teams=teams, seasons=seasons, user=current_user,league=league, season=season)
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
        
        return redirect(url_for('views.edit_league', leagueid=league.id))
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
                goal = Goal(amount=team2_scorers[c], scorer_id=player.id, match_id=match.id, team_id=team2_id)
                db.session.add(goal)
                db.session.commit()
            c+=1
        
        league = League.query.get(leagueid)
        seasons = Season.query.get(seasonid)
        return redirect(url_for('views.edit_league', leagueid=league.id))

    
    
    
    
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
    
    return redirect(url_for('views.edit_league', leagueid=league.id))

    


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
