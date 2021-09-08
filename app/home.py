from flask import Blueprint, render_template, request, session, current_app, make_response, url_for, flash
from flask_login import current_user
from datetime import datetime, timedelta
from sqlalchemy import or_
from .models import User

home = Blueprint('home', __name__)

# check __init__.py - line 42
"""
@app.before_request
  def check_session():
    if request.path == "/": return

    if session.get("SEARCH_QUERY"):
      del session["SEARCH_QUERY"]
"""

@home.route('/', methods=["GET", "POST"])
def index():
  search = request.args.get("search")
  page = request.args.get("page", 1, type=int)
  per_page = request.args.get("per-page", current_app.config['RESULTS_PER_PAGE'], type=int)

  if not current_user.is_authenticated: current_user.username = ""
  result = User.query.filter(User.username != current_user.username).order_by(User.created.desc()).paginate(page, per_page, True)

  return render_template("main/home.html", result=result)

@home.route("/about")
def about():
  return "about"

@home.route("/contact")
def contact():
  return "contact"