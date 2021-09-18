from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import backref, defaultload, lazyload
from sqlalchemy import or_
from . import db
from flask_login import UserMixin
from flask import current_app
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class Like(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  read = db.Column(db.Boolean, default=False)
  timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

  target_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  def __repr__(self):
    return f'<Like({self.id}, {self.sender.username}, {self.target.username})>'


class Match(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  read_1 = db.Column(db.Boolean, default=False)
  read_2 = db.Column(db.Boolean, default=False)
  timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

  target_1_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  target_2_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  def read_by(self, user):
    if self.target_1 == user:
      return self.read_1
    elif self.target_2 == user:
      return self.read_2
    return None
  
  def other(self, user):
    if self.target_1 == user:
      return self.target_2
    elif self.target_2 == user:
      return self.target_1
    return None

  def __repr__(self):
    return f'<Match({self.id}, {self.target_1.username}, {self.target_2.username})>'


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
  full_name = db.Column(db.String(128))
  birthday = db.Column(db.Date)
  gender = db.Column(db.String(512), default="not specified")
  description = db.Column(db.String(1000), default="not specified")
  meme_taste = db.Column(db.String(512), default="not specified")
  country = db.Column(db.String(100), default="not specified")
  city = db.Column(db.String(100), default="not specified")
  created = db.Column(db.DateTime(), default=datetime.utcnow)
  last_online = db.Column(db.DateTime(), default=datetime.utcnow)
  confirmed = db.Column(db.Boolean, default=False)
  profile_pic = db.Column(db.String(255), default="default.png")
  password_hash = db.Column(db.String(128))

  meme_1 = db.Column(db.String(255), default="meme.png")
  meme_2 = db.Column(db.String(255), default="meme.png")
  meme_3 = db.Column(db.String(255), default="meme.png")

  like_inbox = db.relationship("Like", foreign_keys='Like.target_id', backref='target', lazy="dynamic")
  like_sent = db.relationship("Like", foreign_keys='Like.sender_id', backref='sender', lazy="dynamic")
  
  match_1 = db.relationship("Match", foreign_keys='Match.target_1_id', backref='target_1', lazy="dynamic")
  match_2 = db.relationship("Match", foreign_keys='Match.target_2_id', backref='target_2', lazy="dynamic")

  msg_inbox = db.relationship("Message", foreign_keys='Message.target_id', backref='target', lazy="dynamic")
  msg_sent = db.relationship("Message", foreign_keys='Message.sender_id', backref='sender', lazy="dynamic")

  def is_match(self, user):
    m1 = self.match_1.filter(Match.target_2 == user).first()
    m2 = self.match_2.filter(Match.target_1 == user).first()
    return m1 or m2
  
  def liking(self, user):
    return self.like_sent.filter(Like.target == user).count() > 0

  def like(self, user):
    if self.like_sent.filter(Like.target == user).count() > 0:
      return
    if self == user:
      return
    l = Like(sender=self, target=user)

    if self.like_inbox.filter(Like.sender == user).first():
      m = Match(target_1=self, target_2=user)
      db.session.add(m)

    db.session.add(l)
    db.session.commit()

  def dislike(self, user):
    if self.like_sent.filter(Like.sender == self).count() == 0:
      return
    if self == user:
      return

    if self.is_match(user):
      db.session.delete(self.is_match(user))

    l = self.like_sent.filter(Like.target == user).first()

    db.session.delete(l)
    db.session.commit()
  
  def new_likes(self):
    return self.like_inbox.filter(Like.read == False).count()
  
  def new_matches(self):
    m1 = self.match_1.filter(Match.read_1 == False).count()
    m2 = self.match_2.filter(Match.read_2 == False).count()

    return m1 + m2

  def new_messages(self, sender=None):
    if sender:
      return self.msg_inbox.filter(Message.read == False, Message.sender == sender).count()
    return self.msg_inbox.filter(Message.read == False).count()
  
  def contacts(self):
    senders = set(map(lambda m: m.sender, self.msg_inbox.all()))
    receivers = set(map(lambda x: x.target, self.msg_sent.all()))
    return sorted(senders.union(receivers), key=lambda x:x.chat(self)[-1].timestamp, reverse=True)
  
  def chat(self, target):
    messages = Message.query.filter(or_(Message.target == self, Message.sender == self))\
      .filter(or_(Message.target == target, Message.sender == target))
    
    return messages.order_by(Message.timestamp.asc()).limit(current_app.config["LOAD_MESSAGES"]).all()
  
  def send_message(self, content, target):
    msg = Message(content=content, sender=self, target=target)
    db.session.add(msg)
    db.session.commit()

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

  def get_token(self, command, expire_sec=1800):
    s = Serializer(current_app.config['SECRET_KEY'], expire_sec)
    return s.dumps({'user_id': self.id, 'command': command}).decode('utf-8')
  
  @staticmethod
  def verify_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
      data = s.loads(token)
    except:
      return None, None
    return User.query.get(data['user_id']), data['command']

  def __repr__(self):
    return f'<User({self.id}, {self.username}, {self.email})>'