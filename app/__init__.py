from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_migrate import Migrate
from .config import Config


db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
csrf = CSRFProtect()

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
  from .models import User, Message

  app = Flask(__name__)
  app.config.from_object(Config)

  @app.context_processor
  def globals():
    return {}

  @app.before_request
  def check_session():
    if request.path == "/": return

    if session.get("SEARCH_QUERY"):
      del session["SEARCH_QUERY"]
  
  @app.cli.command("create-db")
  def create_user():
    u = User()
    u.username = "example"
    u.email = "example@example.com"
    u.first_name = "John"
    u.last_name = "smith"
    u.password = "12345678"

    m = Message()
    m.content = "Hello world!"
    m.sender = u
    m.target = u

    db.session.add(u)
    db.session.add(m)

    db.session.commit()

  db.init_app(app)
  db.create_all(app=app)
  mail.init_app(app)
  migrate.init_app(app, db)
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
  
  return app