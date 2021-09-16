from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user, logout_user, login_user
from datetime import date
import re
from .models import User
from .utils import valid_date, valid_email
from . import db


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for("profile.prof", username=current_user.username))

  if request.method == "POST":
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()
    if user and user.verify_password(password):
      login_user(user, remember=True)
      flash("Logged in successfully.", category="success")
      
      next = request.args.get('next')

      return redirect(next or url_for("profile.prof", username=user.username))
    else :
      flash("Invalid username or password. Try again.", category="error")

  return render_template("auth/login.html")


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
  if current_user.is_authenticated:
    return render_template("profile.prof", username=current_user.username)
  
  if request.method == "POST":
    email = request.form.get('email').strip()
    username = request.form.get('username').strip()
    full_name = request.form.get('full-name').strip()
    birthday = request.form.get('birthday').strip()
    password1 = request.form.get('password-1').strip()
    password2 = request.form.get('password-2').strip()

    if not valid_email(email):
      flash("This email is invalid or already exists. Try another one.", category="error")
    elif False: # valid_username()
      flash("This username already exists. Try another one.", category="error")
    elif not re.search(r"\S{2,}", full_name):
      flash("Name is too short.", category="error")
    elif not valid_date(birthday):
      flash("Error while reading date of birth. Try again.")
    elif len(password1) < 8:
      pass
    elif password1 != password2:
      pass
    else:
      user = User()
      user.email = email
      user.username = username
      user.full_name = full_name
      user.birthday = date.fromisoformat(birthday)
      user.password = password1

      db.session.add(user)
      db.session.commit()

      login_user(user, remember=True)
      flash("Account created successfullly! Please edit your profile...", category="success")

      return redirect(url_for("profile.prof", username=user.username))

  return render_template("auth/signup.html")


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
  logout_user()
  flash('Logged out successfully!', category='success')
  return redirect(url_for('home.index'))
