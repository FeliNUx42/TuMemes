from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_recaptcha import ReCaptcha
from flask_talisman import Talisman
from .config import Config


db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
moment = Moment()
csrf = CSRFProtect()
recaptcha = ReCaptcha()
talisman = Talisman()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = "error"
login_manager.refresh_view = "/login?reauth=1"
login_manager.needs_refresh_message_category = "error"

@login_manager.user_loader
def load_user(id):
  from .models import User
  return User.query.get(int(id))


def create_app():
  from .models import User, Like, Match, Message

  app = Flask(__name__)
  app.config.from_object(Config)

  @app.context_processor
  def globals():
    return {
      "enumerate": enumerate
    }

  @app.before_request
  def check_session():
    if request.endpoint == "home.index": return
    if request.endpoint == "static": return

    if session.get("SEARCH_QUERY"):
      del session["SEARCH_QUERY"]
  
  @app.after_request
  def read_things(response):
    if request.endpoint == "profile.likes":
      for like in current_user.like_inbox.all():
        like.read = True
      
      db.session.commit()
    
    if request.endpoint == "profile.matches":
      matches = current_user.match_1.union(current_user.match_2).all()
      for match in matches:
        if match.target_1 == current_user:
          match.read_1 = True
        else:
          match.read_2 = True
      
      db.session.commit()
    
    if request.endpoint == "profile.inbox":
      for msg in current_user.msg_inbox.all():
        msg.read = True
      
      db.session.commit()
    
    return response
  
  @app.cli.command("create-db")
  def create_db():
    from .utils import create_user
    for _ in range(3):
      create_user()

  db.init_app(app)
  db.create_all(app=app)
  mail.init_app(app)
  migrate.init_app(app, db)
  moment.init_app(app)
  login_manager.init_app(app)
  csrf.init_app(app)
  recaptcha.init_app(app)
  if app.config["HEROKU"]:
    talisman.init_app(app)

  from .home import home
  from .auth import auth
  from .profile import profile
  from .errors import errors

  app.register_blueprint(home)
  app.register_blueprint(auth)
  app.register_blueprint(profile)
  app.register_blueprint(errors)

  with app.app_context():
    if db.engine.url.drivername == 'sqlite':
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)
  
  return app