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

def get_result():
  name = request.form.get("name")
  description = request.form.get("description")
  #gender = request.form.get("gender")
  memes = request.form.get("memes")
  min_age = request.form.get("min-age")
  max_age = request.form.get("max-age")
  country = request.form.get("country")
  city = request.form.get("city")

  result = User.query

  if name:
    result = result.filter(User.full_name.ilike(f"%{name}%"))
  if description:
    result = result.filter(User.description.ilike(f"%{description}%"))
  #if gender:
  #  result = result.filter(User.gender.ilike(f"%{gender}%"))
  if memes:
    result = result.filter(User.meme_taste.ilike(f"%{memes}%"))
  if min_age and min_age.isnumeric():
    bday = datetime.now() - timedelta(days=365*(int(min_age)-1))
    result = result.filter(User.birthday <= bday)
  if max_age and max_age.isnumeric():
    bday = datetime.now() - timedelta(days=365*(int(max_age)+1))
    result = result.filter(User.birthday >= bday)
  if country:
    result = result.filter(User.country.ilike(f"%{country}%"))
  if city:
    result = result.filter(User.city.ilike(f"%{city}%"))
    
  return result


@home.route('/', methods=["GET", "POST"])
def index():
  search = request.args.get("search")
  page = request.args.get("page", 1, type=int)
  per_page = request.args.get("per-page", current_app.config['RESULTS_PER_PAGE'], type=int)

  if not current_user.is_authenticated: current_user.username = ""
  result = get_result().order_by(User.created.desc()).paginate(page, per_page, True)

  return render_template("main/home.html", result=result)

@home.route("/about")
def about():
  return "about"

@home.route("/contact")
def contact():
  return "contact"