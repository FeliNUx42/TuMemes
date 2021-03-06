from flask import current_app, flash, redirect, url_for
from flask_login import current_user
from .models import User
from . import db
from string import ascii_letters
from functools import wraps
from datetime import date
from uuid import uuid4
from PIL import Image
from os import path
import names
import re


def valid_username(username, id=0):
  from .models import User

  user = User.query.filter_by(username=username).first()
  pages = list(current_app.url_map.iter_rules())
  _pages = [p.rule.split("/")[-1] for p in pages if not p.arguments]
  
  if user and user.id != id:
    return False

  if username in _pages or "/" in username:
    return False

  return True

def valid_email(email):
  pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
  type = re.search(pattern, email)
  user = User.query.filter_by(email=email).first()

  return not user and type

def valid_picture(file):
  extensions = (".png", ".jpg", ".jpeg")
  for ext in extensions:
    if file.filename.endswith(ext):
      return True
  return False

def save_file(form_pic, meme=False):
  hex = uuid4().hex
  _, ext = path.splitext(form_pic.filename)
  picture_fn = hex + ext
  if meme:
    picture_path = path.join(current_app.root_path, current_app.config["MEME_PICTURE_FOLDER"], picture_fn)
  else:
    picture_path = path.join(current_app.root_path, current_app.config["PROFILE_PICTURE_FOLDER"], picture_fn)

  output_size = (600, 600)
  i = Image.open(form_pic)
  i.thumbnail(output_size)
  i.save(picture_path)

  return picture_fn

def valid_date(birthday:str):
  try:
    _ = date.fromisoformat(birthday)
    return True
  except:
    return False

def create_user():
  u = User()
  f = names.get_first_name()
  l = names.get_last_name()
  if current_app.config["AUTO_CONFIRM"]:
    u.email = f"{f}.{l}@gmail.mom"
    u.confirmed = True
  else:
    u.email = current_app.config["MAIL_USERNAME"]
  u.username = f"{f}-{l}"
  u.full_name = f"{f} {l}"
  u.birthday = date(2001, 1, 1)
  u.password = "12345678"

  db.session.add(u)
  db.session.commit()

def confirmed_required(func):
  @wraps(func)
  def decorated_function(*args, **kwargs):
    if not current_user.confirmed:
      flash('Please confirm your account!', 'error')
      return redirect(url_for('auth.unconfirmed'))
    return func(*args, **kwargs)

  return decorated_function
