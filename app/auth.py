from os import error
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user, logout_user, login_user
import re
from .models import User
from .utils import valid_email
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
      return redirect(url_for("profile.prof", username=current_user.username))
    else :
      flash("Invalid username or password. Try again.", category="error")

  return render_template("auth/login.html")


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
  if current_user.is_authenticated:
    return render_template("profile.prof", username=current_user.username)
  
  if request.method == "POST":
    email = request.form.get('email')
    username = request.form.get('username')
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')

    if not valid_email(email):
      flash("This email is invalid or already exists. Try another one.", category="error")
    elif False: # valid_username()
      flash("This username already exists. Try another one.", category="error")
    elif not re.search(r"\S{2,}", first_name):
      flash("First Name is too short.", category="error")
    elif not re.search(r"\S{2,}", last_name):
      flash("Last Name is too short.", category="error")
    elif len(password1) < 8:
      pass
    elif password1 != password2:
      pass
    else:
      user = User()
      user.email = email
      user.username = username
      user.first_name = first_name
      user.last_name = last_name
      user.password = password1

      db.session.add(user)
      db.session.commit()

      login_user(user, remember=True)
      flash("Account created successfullly!", category="success")

      return redirect(url_for("profile.prof", username=user.username))

  return render_template("auth/signup.html")


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
  logout_user()
  flash('Logged out successfully!', category='success')
  return redirect(url_for('home.index'))
