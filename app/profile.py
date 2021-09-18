from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, current_app
from flask_login import login_required, current_user, fresh_login_required, logout_user
import re
from .models import Match, Message, User, Like
from .utils import save_file, valid_picture
from . import db

profile = Blueprint('profile', __name__)

@profile.route('/<username>', methods=['GET', 'POST'])
def prof(username):
  user = User.query.filter_by(username=username).first_or_404()

  return render_template("profile/profile.html", author=user)

@profile.route('/<username>/settings', methods=['GET', 'POST'])
@fresh_login_required
def settings(username):
  user = User.query.filter_by(username=username).first_or_404()

  if current_user != user:
    abort(403)

  if request.method == "POST":
    username = request.form.get("username").strip() or ""
    full_name = request.form.get("full-name").strip() or ""
    gender = request.form.get("gender").strip() or "not specified"
    city = request.form.get("city").strip() or "not specified"
    country = request.form.get("country").strip() or "not specified"
    description = request.form.get("description").strip() or "not specified"
    meme_taste = request.form.get("meme-taste").strip() or "not specified"

    profile_pic = request.files.get("profile-pic")
    meme_1 = request.files.get("meme-1")
    meme_2 = request.files.get("meme-2")
    meme_3 = request.files.get("meme-3")

    change_pwd = request.form.get("activate-pwd") == "on"
    password1 = request.form.get("password-1")
    password2 = request.form.get("password-2")

    if False: # valid_username()
      flash("This username already exists. Try another one.", category="error")
    elif not re.search(r"\S{2,}", full_name):
      flash("Name is too short.", category="error")
    elif len(description) < 10:
      flash("Description is too short.", category="error")
    else:
      user.username = username
      user.full_name = full_name
      user.gender = gender
      user.city = city
      user.country = country
      user.meme_taste = meme_taste
      user.description = description

      if profile_pic.filename:
        if valid_picture(profile_pic):
          user.profile_pic = save_file(profile_pic)
        else:
          flash(f"'{profile_pic.filename}' is not a valid file type. Only .png, .jpg and .jpeg are accepted.", category="error")
      
      if meme_1.filename:
        if valid_picture(meme_1):
          user.meme_1 = save_file(meme_1, meme=True)
        else:
          flash(f"'{meme_1.filename}' is not a valid file type. Only .png, .jpg and .jpeg are accepted.", category="error")
      
      if meme_2.filename:
        if valid_picture(meme_2):
          user.meme_2 = save_file(meme_2, meme=True)
        else:
          flash(f"'{meme_2.filename}' is not a valid file type. Only .png, .jpg and .jpeg are accepted.", category="error")
      
      if meme_3.filename:
        if valid_picture(meme_3):
          user.meme_3 = save_file(meme_3, meme=True)
        else:
          flash(f"'{meme_3.filename}' is not a valid file type. Only .png, .jpg and .jpeg are accepted.", category="error")
      
      if change_pwd:
        if len(password1) < 8:
          flash("Password must at least 8 characters long.", category="error")
        elif password1 != password2:
          flash("Passwords don't match.", category="error")
        else:
          user.password = password1
      
      db.session.commit()
      flash("Data updated successfully!", category="success")

      return redirect(url_for("profile.prof", username=user.username))
    

  return render_template("profile/settings.html")


@profile.route('/<username>/like', methods=['POST'])
@login_required
def like(username):
  user = User.query.filter_by(username=username).first_or_404()

  if current_user != user:
    abort(403)

  target_username = request.form.get("target")
  target = User.query.filter_by(username=target_username).first()

  if not target:
    abort(500)

  match = current_user.is_match(target)

  if user.liking(target):
    user.dislike(target)
  else:
    user.like(target)
  
  if match != current_user.is_match(target):
    return "reload"

  return "success"

@profile.route('/<username>/likes')
@login_required
def likes(username):
  page = request.args.get("page", 1, type=int)
  user = User.query.filter_by(username=username).first_or_404()

  if current_user != user:
    abort(403)
  
  likes = user.like_inbox.order_by(Like.timestamp.desc()).paginate(page, current_app.config['RESULTS_PER_PAGE'], True)

  return render_template("profile/likes.html", likes=likes)

@profile.route('/<username>/inbox', methods=["GET", "POST"])
@login_required
def inbox(username):
  user = User.query.filter_by(username=username).first_or_404()

  if current_user != user:
    abort(403)
  
  if request.method == "POST":
    target = request.form.get("target")
    content = request.form.get("content")

    content = content.replace("\n", "<br>")

    target = User.query.filter_by(username=target).first_or_404()
    msg = Message(content=content, sender=current_user, target=target)

    if not current_user.is_match(target):
      abort(403)

    db.session.add(msg)
    db.session.commit()
  
  new_sender = None
  if request.method == "GET":
    new_sender = User.query.filter_by(username=request.args.get("target")).first()

    if new_sender and not current_user.is_match(new_sender):
      abort(403)

    if new_sender in current_user.contacts():
      new_sender = None
  
  return render_template("profile/inbox.html", new_sender=new_sender)

@profile.route('/<username>/matches')
@login_required
def matches(username):
  page = request.args.get("page", 1, type=int)
  user = User.query.filter_by(username=username).first_or_404()

  if current_user != user:
    abort(403)
  
  matches = user.match_1.union(user.match_2)
  matches = matches.order_by(Match.timestamp.desc()).paginate(page, current_app.config['RESULTS_PER_PAGE'], True)

  return render_template("profile/matches.html", matches=matches)