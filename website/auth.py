from flask import Blueprint, render_template, request, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db 
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        emailusername = request.form.get("email")
        password =  request.form.get("password")
        
        emailusername = "orvol905@gmail.com"
        password="leka1330"
        
        if "@" in emailusername:
            user = User.query.filter_by(email=emailusername).first()
        else:
            user = User.query.filter_by(username=emailusername).first()
            
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
    
        return render_template("login.html", message="Incorrect password or username!") 
        
    else:
        return render_template("login.html")

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))

@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            return render_template("signup.html", message="Email already exists.") 
        elif len(email) < 4:
            return render_template("signup.html", message="Email must be greater than 3 characters.") 
        elif len(username) < 2:
            return render_template("signup.html", message="Username must be longer than 1 character")
        elif password1 != password2:
            return render_template("signup.html", message="Passwords dont\'t match.")
        elif len(password1) < 7:
            return render_template("signup.html", message="Password must be at least 7 characters.")
        
        new_user = User(email=email, username=username, password=generate_password_hash(password1))
        db.session.add(new_user)
        db.session.commit()
        
        
        return redirect(url_for("auth.login"))
    else:
        return render_template("signup.html")