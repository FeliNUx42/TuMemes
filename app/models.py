from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import backref, defaultload, lazyload
from . import db
from flask_login import UserMixin
from flask import current_app
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(128), unique=True)
  username = db.Column(db.String(128), unique=True)
  first_name = db.Column(db.String(128))
  last_name = db.Column(db.String(128))
  description = db.Column(db.String(1000), default="No description...")
  created = db.Column(db.DateTime(), default=datetime.utcnow)
  last_online = db.Column(db.DateTime(), default=datetime.utcnow)
  profile_pic = db.Column(db.String(255), default="default.png")
  password_hash = db.Column(db.String(128))

  meme_1 = db.Column(db.String(255), default="meme.png")
  meme_2 = db.Column(db.String(255), default="meme.png")
  meme_3 = db.Column(db.String(255), default="meme.png")

  inbox = db.relationship("Message", foreign_keys='Message.target_id', backref='target', lazy="dynamic")
  sent = db.relationship("Message", foreign_keys='Message.sender_id', backref='sender', lazy="dynamic")

  @property
  def password(self):
    raise AttributeError("password is not a readable attribute")

  @password.setter
  def password(self, password):
    self.password_hash = generate_password_hash(password)
  
  def verify_password(self, password):
    return check_password_hash(self.password_hash, password)

  def __repr__(self):
    return f'<User({self.id}, {self.username}, {self.email})>'


class Message(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.String(4096))
  read = db.Column(db.Boolean, default=False)
  timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

  target_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  def __repr__(self):
    return f'<Message({self.id}, {self.content})>'