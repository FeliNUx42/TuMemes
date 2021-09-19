from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, current_app
from flask_login import login_required, current_user, fresh_login_required, logout_user
import re
import os
from .models import Match, Message, User, Like
from .utils import save_file, valid_picture, confirmed_required, valid_username
from .email import send_delete_email
from . import db

profile = Blueprint('profile', __name__)

@profile.route('/<username>', methods=['GET', 'POST'])
def prof(username):
  user = User.query.filter_by(username=username).first_or_404()

  return render_template("profile/profile.html", author=user)

@profile.route('/<username>/settings', methods=['GET', 'POST'])
@fresh_login_required
@confirmed_required
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

    if not valid_username(username, user.id):
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
@confirmed_required
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
@confirmed_required
def likes(username):
  page = request.args.get("page", 1, type=int)
  user = User.query.filter_by(username=username).first_or_404()

  if current_user != user:
    abort(403)
  
  likes = user.like_inbox.order_by(Like.timestamp.desc()).paginate(page, current_app.config['RESULTS_PER_PAGE'], True)

  return render_template("profile/likes.html", likes=likes)

@profile.route('/<username>/inbox', methods=["GET", "POST"])
@login_required
@confirmed_required
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
@confirmed_required
def matches(username):
  page = request.args.get("page", 1, type=int)
  user = User.query.filter_by(username=username).first_or_404()

  if current_user != user:
    abort(403)
  
  matches = user.match_1.union(user.match_2)
  matches = matches.order_by(Match.timestamp.desc()).paginate(page, current_app.config['RESULTS_PER_PAGE'], True)

  return render_template("profile/matches.html", matches=matches)

@profile.route('/<username>/delete-account')
@login_required
@confirmed_required
def deleteacc(username):
  user = User.query.filter_by(username=username).first_or_404()
  
  if user != current_user:
    abort(403)

  send_delete_email(user)
  flash('An email has been sent with instructions to delete your account.', category='success')

  return redirect(url_for("profile.prof", username=user.username))

@profile.route('/<username>/delete-account/<token>', methods=['GET', 'POST'])
@login_required
@confirmed_required
def delete_confirm(username, token):
  _user = User.query.filter_by(username=username).first_or_404()
  user, command = User.verify_token(token)
  if user is None or command != 'delete-account':
    flash('That is an expired or invalid token.', category='error')
    return redirect(url_for('profile.deleteacc', username=_user.username))
  
  if user != current_user or user != _user:
    abort(403)

  if request.method == "POST":
    delete = request.form.get('yes')
    if delete is None:
      return redirect(url_for("profile.prof", username=user.username))
    
    logout_user()

    for l in user.like_inbox.all():
      db.session.delete(l)
    
    for l in user.like_sent.all():
      db.session.delete(l)
    
    for m in user.match_1.all():
      db.session.delete(m)
    
    for m in user.match_2.all():
      db.session.delete(m)
    
    for msg in user.msg_inbox.all():
      db.session.delete(msg)
    
    for msg in user.msg_sent.all():
      db.session.delete(msg)

    img_path = os.path.join(current_app.root_path, current_app.config["PROFILE_PICTURE_FOLDER"], user.profile_pic)
    if not img_path.endswith("/default.png"):
      os.remove(img_path)
    
    meme_1 = os.path.join(current_app.root_path, current_app.config["MEME_PICTURE_FOLDER"], user.meme_1)
    if not meme_1.endswith("/meme.png"):
      os.remove(meme_1)
    
    meme_2 = os.path.join(current_app.root_path, current_app.config["MEME_PICTURE_FOLDER"], user.meme_2)
    if not meme_2.endswith("/meme.png"):
      os.remove(meme_2)
    
    meme_3 = os.path.join(current_app.root_path, current_app.config["MEME_PICTURE_FOLDER"], user.meme_3)
    if not meme_3.endswith("/meme.png"):
      os.remove(meme_3)

    db.session.delete(user)
    db.session.commit()

    flash('Account deleted successfully!', category='success')
    return redirect(url_for('home.index'))

  return render_template("profile/deleteacc.html", author=user)