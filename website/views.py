from flask import Blueprint, render_template
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    if current_user:
        return render_template("home.html", user=current_user)
    else:
        return render_template("login.html", user=current_user)