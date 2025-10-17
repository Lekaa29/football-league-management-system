# Sports League Management System

A Flask-based web application for managing sports leagues, teams, players, and match results.

## Features

- **League Management** - Create and edit leagues with season tracking
- **Team Management** - Add teams to leagues, manage rosters
- **Player Profiles** - Comprehensive player information and statistics
- **Match Results** - Record and display game outcomes
- **User Authentication** - Secure login and registration system
- **Season Tracking** - Multi-season support for historical data

## Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML templates with Jinja2
- **Authentication:** Flask session management
- **Database:** SQLite/PostgreSQL (configurable)


## Project Structure

```
├── views.py              # Route handlers and business logic
├── templates/
│   ├── layout.html       # Base template
│   ├── home.html         # Landing page
│   ├── login.html        # User authentication
│   ├── signup.html       # User registration
│   ├── addleague.html    # League creation
│   ├── leaguemain.html   # League dashboard
│   ├── add-season.html   # Season management
│   ├── addteam.html      # Team creation
│   ├── team-main.html    # Team dashboard
│   ├── add_player.html   # Player registration
│   ├── player-main.html  # Player profile
│   ├── add_result.html   # Match result entry
│   └── match_main.html   # Match overview
├── static/               # CSS, JS, images
└── models.py             # Database models
```

## Core Functionality

### Routes

```python
GET  /                    # Landing page
GET  /home               # User dashboard
GET  /login              # Authentication
POST /login              # Process login

# League Management
GET  /addleague          # Create league form
POST /addleague          # Process league creation
GET  /league/<id>        # League details
POST /edit_league        # Update league
POST /add_season         # Create new season

# Team Management
GET  /addteam            # Add team form
POST /addteam            # Process team addition
GET  /team/<id>          # Team dashboard
POST /remove_team        # Remove team from league

# Player Management
GET  /add_player         # Player registration form
POST /add_player         # Process player addition
GET  /player/<id>        # Player profile

# Match Management
GET  /add_result         # Record match result
POST /add_result         # Process match result
GET  /match/<id>         # Match details
```

## Database Schema

### Core Models
- **User** - Authentication and user profiles
- **League** - League configuration and metadata
- **Season** - Seasonal divisions within leagues
- **Team** - Team information and statistics
- **Player** - Player profiles and data
- **Match** - Game results and outcomes


## Future Enhancements

- Real-time statistics calculation
- Export data to CSV/PDF
- Advanced search and filtering
- Mobile-responsive design
- REST API for external integrations

---

**Last Updated:** 2023  
