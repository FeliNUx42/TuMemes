from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from datetime import date
from .config import Config


db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
moment = Moment()
csrf = CSRFProtect()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = "error"
login_manager.refresh_view = "/login?reauth=1"
login_manager.needs_refresh_message_category = "error"

@login_manager.user_loader
def load_user(id):
  from .models import User, Match, Message
  return User.query.get(int(id))


def create_app():
  from .models import User, Message

  app = Flask(__name__)
  app.config.from_object(Config)

  @app.context_processor
  def globals():
    return {
      "enumerate": enumerate
    }

  @app.before_request
  def check_session():
    if request.path == "/": return

    if session.get("SEARCH_QUERY"):
      del session["SEARCH_QUERY"]
  
  @app.after_request
  def read_things(response):
    if request.endpoint == "profile.matches":
      for match in current_user.match_inbox.all():
        match.read = True
      
      db.session.commit()
    
    if request.endpoint == "profile.inbox":
      for msg in current_user.msg_inbox.all():
        msg.read = False #change
      
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