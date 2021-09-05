from flask import Blueprint, render_template, request, session, current_app, make_response, url_for
from datetime import datetime, timedelta
from flask.helpers import flash
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

@home.route('/')
def index():
  return render_template("main/home.html")

@home.route("/about")
def about():
  return "about"

@home.route("/contact")
def contact():
  return "contact"