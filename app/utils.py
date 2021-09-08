from flask import current_app
from .models import User
from . import db
from string import ascii_letters
from datetime import date
from uuid import uuid4
from PIL import Image
from os import path
import random
import re


def valid_email(email):
  pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
  return re.search(pattern, email)

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
  def string(length):
    char = ""
    for _ in range(length):
      char += random.choice(ascii_letters)
    return char
  
  u = User()
  u.email = string(20)
  u.username = string(10)
  u.first_name = string(6)
  u.last_name = string(6)
  u.birthday = date(2001, 1, 1)
  u.password = "12345678"

  db.session.add(u)
  db.session.commit()
