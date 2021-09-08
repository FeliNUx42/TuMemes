from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import backref, defaultload, lazyload
from . import db
from flask_login import UserMixin
from flask import current_app
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class Match(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  read = db.Column(db.Boolean, default=False)
  timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

  target_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  def __repr__(self):
    return f'<Match({self.id}, {self.sender.username}, {self.target.username})>'


class Message(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.String(4096))
  read = db.Column(db.Boolean, default=False)
  timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

  target_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  def __repr__(self):
    return f'<Message({self.id}, {self.content}, {self.sender.username}, {self.target.username})>'


class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(128), unique=True)
  username = db.Column(db.String(128), unique=True)
  first_name = db.Column(db.String(128))
  last_name = db.Column(db.String(128))
  birthday = db.Column(db.Date)
  description = db.Column(db.String(1000), default="not specified")
  meme_taste = db.Column(db.String(512), default="not specified")
  country = db.Column(db.String(100), default="not specified")
  city = db.Column(db.String(100), default="not specified")
  created = db.Column(db.DateTime(), default=datetime.utcnow)
  last_online = db.Column(db.DateTime(), default=datetime.utcnow)
  profile_pic = db.Column(db.String(255), default="default.png")
  password_hash = db.Column(db.String(128))

  meme_1 = db.Column(db.String(255), default="meme.png")
  meme_2 = db.Column(db.String(255), default="meme.png")
  meme_3 = db.Column(db.String(255), default="meme.png")

  match_inbox = db.relationship("Match", foreign_keys='Match.target_id', backref='target', lazy="dynamic")
  match_sent = db.relationship("Match", foreign_keys='Match.sender_id', backref='sender', lazy="dynamic")

  msg_inbox = db.relationship("Message", foreign_keys='Message.target_id', backref='target', lazy="dynamic")
  msg_sent = db.relationship("Message", foreign_keys='Message.sender_id', backref='sender', lazy="dynamic")

  def is_matching(self, user):
    inbox = self.match_inbox.filter(Match.sender == user).count() > 0
    sent = self.match_sent.filter(Match.target == user).count() > 0
    return inbox and sent

  def match(self, user):
    if self.match_sent.filter(Match.sender == self).count() > 0:
      return
    if self == user:
      return
    self.match_sent.append(user)

  def unmatch(self, user):
    if self.match_sent.filter(Match.sender == self).count() == 0:
      return
    if self == user:
      return
    self.match_sent.remove(user)
  
  def new_matches(self):
    return self.match_inbox.filter(Match.read == False).count()
  
  def new_messages(self):
    return self.msg_inbox.filter(Message.read == False).count()

  @property
  def password(self):
    raise AttributeError("password is not a readable attribute")

  @password.setter
  def password(self, password):
    self.password_hash = generate_password_hash(password)
  
  def verify_password(self, password):
    return check_password_hash(self.password_hash, password)
  
  @property
  def age(self):
    today = datetime.utcnow()
    return today.year - self.birthday.year - \
      ((today.month, today.day) < (self.birthday.month, self.birthday.day))

  def __repr__(self):
    return f'<User({self.id}, {self.username}, {self.email})>'